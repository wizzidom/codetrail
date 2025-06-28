from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import ast
from pathlib import Path
import shutil
import zipfile
import tempfile
import openai
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from summarizers import generate_function_summary
from fastapi.middleware.cors import CORSMiddleware




# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI()  # Uses OPENAI_API_KEY from env

# Create FastAPI app instance
app = FastAPI()
#Allow certain ports for my frontend I am using 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------------------------------
# Function: Parse a Python file for functions
# -------------------------------
def parse_python_file(file_path: Path):
    """
    Parses a Python file and returns a list of all function definitions,
    including name, argument names, and the full source code of each function.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    # Parse the file into an abstract syntax tree (AST)
    tree = ast.parse(source)
    functions = []

    # Traverse all nodes in the AST tree
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            args = [arg.arg for arg in node.args.args]

            # Safely extract function source code using line numbers
            lines = source.splitlines()
            func_lines = lines[node.lineno - 1: node.end_lineno]
            func_source = "\n".join(func_lines)

            # Append function data to list
            functions.append({
                "name": func_name,
                "args": args,
                "source": func_source
            })

    return functions

# -------------------------------
# Function: Generate GPT summary for a function
# -------------------------------



# async def generate_function_summary(function_code: str) -> str:
#     prompt = f"Summarize what this Python function does in a clear and concise sentence:\n\n{function_code}"

#     response = await client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant who summarizes Python functions."},
#             {"role": "user", "content": prompt},
#         ],
#         max_tokens=60,
#         temperature=0.2,
#     )

#     return response.choices[0].message.content.strip()


# -------------------------------
# Endpoint: Health check
# -------------------------------
@app.get("/")
def read_root():
    """
    Health check route.
    """
    return {"message": "Hello from CodeTrail!"}

# -------------------------------
# Endpoint: Upload ZIP and analyze functions
# -------------------------------
@app.post("/upload/")
async def upload_zip(file: UploadFile = File(...)):
    """
    Accepts a ZIP file containing Python code,
    extracts all `.py` files, parses their functions,
    and generates OpenAI-powered summaries for each one.
    """
    # Validate the uploaded file is a .zip
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed.")

    # Use a temporary directory to avoid saving files permanently
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Save the uploaded ZIP file temporarily in memory
        temp_zip_path = temp_dir_path / file.filename
        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract the contents of the ZIP into the temp directory
        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir_path)

        # Prepare a list of async tasks to process each .py file
        tasks = []

        # Define inner async function to parse + summarize one file
        async def parse_and_summarize(file_path: Path, relative_path: Path):
            # Parse function info from the file
            functions = parse_python_file(file_path)

            # For each function, generate a GPT summary
            for func in functions:
                func['summary'] = await generate_function_summary(func['source'])

            return {
                "file": str(relative_path),
                "functions": functions
            }

        # Walk through extracted directory to find all .py files
        for root, dirs, files in os.walk(temp_dir_path):
            for file_name in files:
                if file_name.endswith(".py"):
                    full_path = Path(root) / file_name
                    relative_path = full_path.relative_to(temp_dir_path)
                    tasks.append(parse_and_summarize(full_path, relative_path))

        # Run all parsing/summarizing tasks concurrently
        parsed_data = await asyncio.gather(*tasks)

    # Return the results as JSON
    return {
        "filename": file.filename,
        "message": "Upload, parsing, and GPT summaries complete!",
        "parsed": parsed_data
    }
