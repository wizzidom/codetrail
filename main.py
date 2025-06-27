from fastapi import FastAPI, UploadFile, File
import os
import ast
from pathlib import Path
import shutil
import zipfile


app = FastAPI()

UPLOAD_DIR = Path("uploaded_zips")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Hello from CodeTrail!"}

@app.post("/upload/")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        return {"error": "Only ZIP files are allowed."}

    file_path = UPLOAD_DIR / file.filename

    # Save the uploaded ZIP file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create a folder to extract files
    extract_dir = UPLOAD_DIR / file.filename.replace(".zip", "")
    extract_dir.mkdir(exist_ok=True)

    # Extract the ZIP
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Parse all .py files in the extracted directory
    parsed_data = []

    for root, dirs, files in os.walk(extract_dir):
        for file_name in files:
            if file_name.endswith(".py"):
                full_path = Path(root) / file_name
                functions = parse_python_file(full_path)
                parsed_data.append({
                    "file": str(full_path.relative_to(extract_dir)),
                    "functions": functions
                })

    return {
        "filename": file.filename,
        "message": "Upload, extraction, and parsing successful!",
        "parsed": parsed_data
    }

# This function parses Python files to extract function names and their arguments.
def parse_python_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            args = [arg.arg for arg in node.args.args]
            functions.append({
                "name": func_name,
                "args": args
            })

    return functions