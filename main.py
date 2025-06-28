# from fastapi import FastAPI, UploadFile, File, HTTPException
# import os
# import ast
# from pathlib import Path
# import shutil
# import zipfile
# import tempfile
# import openai
# import asyncio
# from openai import AsyncOpenAI
# from dotenv import load_dotenv
# from summarizers import generate_function_summary
# from fastapi.middleware.cors import CORSMiddleware
# import time


# # Load environment variables from .env file
# load_dotenv()

# # Set OpenAI API key from environment
# openai.api_key = os.getenv("OPENAI_API_KEY")
# client = AsyncOpenAI()  # Uses OPENAI_API_KEY from env

# # Create FastAPI app instance
# app = FastAPI()
# #Allow certain ports for my frontend I am using 3000
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# # -------------------------------
# # Function: Parse a Python file for functions
# # -------------------------------
# def parse_python_file(file_path: Path):
#     """
#     Parses a Python file and returns a list of all function definitions,
#     including name, argument names, and the full source code of each function.
#     """
#     with open(file_path, "r", encoding="utf-8") as f:
#         source = f.read()

#     # Parse the file into an abstract syntax tree (AST)
#     tree = ast.parse(source)
#     functions = []

#     # Traverse all nodes in the AST tree
#     for node in ast.walk(tree):
#         if isinstance(node, ast.FunctionDef):
#             func_name = node.name
#             args = [arg.arg for arg in node.args.args]

#             # Safely extract function source code using line numbers
#             lines = source.splitlines()
#             func_lines = lines[node.lineno - 1: node.end_lineno]
#             func_source = "\n".join(func_lines)

#             # Append function data to list
#             functions.append({
#                 "name": func_name,
#                 "args": args,
#                 "source": func_source
#             })

#     return functions

# # -------------------------------
# # Function: Generate GPT summary for a function
# # -------------------------------



# # async def generate_function_summary(function_code: str) -> str:
# #     prompt = f"Summarize what this Python function does in a clear and concise sentence:\n\n{function_code}"

# #     response = await client.chat.completions.create(
# #         model="gpt-4o",
# #         messages=[
# #             {"role": "system", "content": "You are a helpful assistant who summarizes Python functions."},
# #             {"role": "user", "content": prompt},
# #         ],
# #         max_tokens=60,
# #         temperature=0.2,
# #     )

# #     return response.choices[0].message.content.strip()


# # -------------------------------
# # Endpoint: Health check
# # -------------------------------
# @app.get("/")
# def read_root():
#     """
#     Health check route.
#     """
#     return {"message": "Hello from CodeTrail!"}

# # -------------------------------
# # Endpoint: Upload ZIP and analyze functions
# # -------------------------------
# @app.post("/upload/")
# async def upload_zip(file: UploadFile = File(...)):
#     start_time = time.perf_counter()  # Start timing

#     if not file.filename.endswith(".zip"):
#         raise HTTPException(status_code=400, detail="Only ZIP files are allowed.")

#     with tempfile.TemporaryDirectory() as temp_dir:
#         temp_dir_path = Path(temp_dir)

#         temp_zip_path = temp_dir_path / file.filename
#         with open(temp_zip_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
#             zip_ref.extractall(temp_dir_path)

#         tasks = []

#         async def parse_and_summarize(file_path: Path, relative_path: Path):
#             functions = parse_python_file(file_path)
#             for func in functions:
#                 func['summary'] = await generate_function_summary(func['source'])
#             return {
#                 "file": str(relative_path),
#                 "functions": functions
#             }

#         for root, dirs, files in os.walk(temp_dir_path):
#             for file_name in files:
#                 if file_name.endswith(".py"):
#                     full_path = Path(root) / file_name
#                     relative_path = full_path.relative_to(temp_dir_path)
#                     tasks.append(parse_and_summarize(full_path, relative_path))

#         parsed_data = await asyncio.gather(*tasks)

#     end_time = time.perf_counter()  # End timing
#     elapsed = end_time - start_time

#     return {
#         "filename": file.filename,
#         "message": f"Upload, parsing, and GPT summaries complete in {elapsed:.2f} seconds!",
#         "parsed": parsed_data,
#         "elapsed_seconds": elapsed
#     }

from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import ast
from pathlib import Path
import shutil
import zipfile
import tempfile
import asyncio
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import time
from summarizers import generate_function_summary

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_python_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            args = [arg.arg for arg in node.args.args]
            lines = source.splitlines()
            func_lines = lines[node.lineno - 1 : node.end_lineno]
            func_source = "\n".join(func_lines)
            functions.append({
                "name": func_name,
                "args": args,
                "source": func_source
            })
    return functions

@app.post("/upload/")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed.")

    start_time = time.perf_counter()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        temp_zip_path = temp_dir_path / file.filename
        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir_path)

        tasks = []

        async def parse_and_summarize(file_path: Path, relative_path: Path):
            functions = parse_python_file(file_path)
            for func in functions:
                try:
                    func['summary'] = await generate_function_summary(func['source'])
                except Exception as e:
                    print(f"Error summarizing function {func['name']}: {e}")
                    func['summary'] = "Summary unavailable due to error."
            return {
                "file": str(relative_path),
                "functions": functions
            }

        for root, dirs, files in os.walk(temp_dir_path):
            for file_name in files:
                if file_name.endswith(".py"):
                    full_path = Path(root) / file_name
                    relative_path = full_path.relative_to(temp_dir_path)
                    tasks.append(parse_and_summarize(full_path, relative_path))

        parsed_data = await asyncio.gather(*tasks)

    end_time = time.perf_counter()
    elapsed = end_time - start_time

    return {
        "filename": file.filename,
        "message": f"Upload, parsing, and GPT summaries complete in {elapsed:.2f} seconds!",
        "parsed": parsed_data,
        "elapsed_seconds": elapsed
    }

