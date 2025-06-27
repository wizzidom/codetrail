from fastapi import FastAPI, UploadFile, File
import os
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


    return {
        "filename": file.filename,
        "message": "Upload and extraction successful!",
        "extracted_to": str(extract_dir)
    }
