from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from app.config import settings
ALLOWED = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
async def save_upload(file: UploadFile | None) -> str | None:
    if not file or not file.filename: return None
    if file.content_type not in ALLOWED: raise HTTPException(400, "Only JPG, PNG, WEBP and PDF files are allowed.")
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(400, f"File must be {settings.max_upload_mb} MB or smaller.")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".pdf"}: raise HTTPException(400, "Unsupported file extension.")
    folder = Path(settings.upload_dir); folder.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}{suffix}"; (folder / name).write_bytes(data)
    return f"/uploads/{name}"
