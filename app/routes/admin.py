import csv, io, time
from collections import defaultdict
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.database import get_db
from app.models import AdminUser, Enquiry, Project
from app.security.authentication import verify_password, require_admin
from app.config import settings
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, File


router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")
_attempts = defaultdict(list)
def render(request, name, **ctx): return templates.TemplateResponse(request=request, name=name, context={"request": request, **ctx})
def admin(request, db): return require_admin(request, db)

@router.get("/login")
def login_page(request: Request): return render(request, "admin/login.html", error=None)

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"; now = time.time()
    _attempts[ip] = [t for t in _attempts[ip] if now - t < 300]
    if len(_attempts[ip]) >= 8: return render(request, "admin/login.html", error="Too many attempts. Try again in five minutes.")
    user = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if not user or not verify_password(password, user.password_hash):
        _attempts[ip].append(now); return render(request, "admin/login.html", error="Invalid username or password.")
    request.session.clear(); request.session["admin_id"] = user.id
    return RedirectResponse("/admin", status_code=303)

@router.post("/logout")
def logout(request: Request): request.session.clear(); return RedirectResponse("/admin/login", status_code=303)

@router.get("")
def dashboard(request: Request, db: Session = Depends(get_db)):
    admin(request, db)
    counts = {s: db.scalar(select(func.count()).select_from(Enquiry).where(Enquiry.status == s)) or 0 for s in ["New", "Contacted", "In Progress", "Completed"]}
    total = db.scalar(select(func.count()).select_from(Enquiry)) or 0
    enquiries = db.scalars(select(Enquiry).order_by(Enquiry.created_at.desc()).limit(30)).all()
    projects = db.scalars(select(Project).order_by(Project.created_at.desc())).all()
    return render(request, "admin/dashboard.html", counts=counts, total=total, enquiries=enquiries, projects=projects)

@router.post("/enquiries/{eid}")
def update_enquiry(eid: int, request: Request, status: str = Form(...), admin_notes: str = Form(""), db: Session = Depends(get_db)):
    admin(request, db); item = db.get(Enquiry, eid)
    if not item: raise HTTPException(404)
    if status not in {"New", "Contacted", "In Progress", "Completed"}: raise HTTPException(422)
    item.status = status; item.admin_notes = admin_notes[:5000]; db.commit()
    return RedirectResponse("/admin#enquiries", status_code=303)

@router.post("/enquiries/{eid}/delete")
def delete_enquiry(eid: int, request: Request, db: Session = Depends(get_db)):
    admin(request, db); item = db.get(Enquiry, eid)
    if item: db.delete(item); db.commit()
    return RedirectResponse("/admin#enquiries", status_code=303)

@router.get("/enquiries.csv")
def export_csv(request: Request, db: Session = Depends(get_db)):
    admin(request, db); rows = db.scalars(select(Enquiry).order_by(Enquiry.created_at.desc())).all()
    output = io.StringIO(); writer = csv.writer(output); writer.writerow(["Reference", "Name", "Email", "Phone", "Service", "Location", "Project Type", "Budget", "Description", "Status", "Created"])
    for e in rows: writer.writerow([e.reference,e.customer_name,e.email,e.phone,e.service,e.location,e.project_type,e.budget,e.description,e.status,e.created_at.isoformat()])
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=dynamicbuilds-enquiries.csv"})

@router.post("/projects")
async def add_project(
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    location: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    admin(request, db)

    image_path = None

    if image and image.filename:
        allowed_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }

        extension = Path(image.filename).suffix.lower()

        if extension not in allowed_types:
            raise HTTPException(400, "Only JPG, PNG and WEBP images are allowed.")

        if image.content_type != allowed_types[extension]:
            raise HTTPException(400, "Invalid image content type.")

        max_bytes = settings.max_upload_mb * 1024 * 1024
        content = await image.read(max_bytes + 1)

        if len(content) > max_bytes:
            raise HTTPException(400, "Image exceeds the 8 MB limit.")

        signatures = {
            ".jpg": content.startswith(b"\xff\xd8\xff"),
            ".jpeg": content.startswith(b"\xff\xd8\xff"),
            ".png": content.startswith(b"\x89PNG\r\n\x1a\n"),
            ".webp": (
                content.startswith(b"RIFF")
                and content[8:12] == b"WEBP"
            )
        }

        if not signatures[extension]:
            raise HTTPException(400, "Invalid image file.")

        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid4().hex}{extension}"
        destination = upload_dir / filename
        destination.write_bytes(content)

        image_path = f"/{settings.upload_dir.replace(chr(92), '/')}/{filename}"

    project = Project(
        title=title[:160],
        category=category[:80],
        description=description,
        location=location[:180] or None,
        image_path=image_path,
        is_published=False,
        is_illustrative=True
    )

    db.add(project)
    db.commit()

    return RedirectResponse("/admin#projects", status_code=303)


@router.post("/projects/{pid}/edit")
async def edit_project(
    pid: int,
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    location: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    admin(request, db)

    project = db.get(Project, pid)
    if not project:
        raise HTTPException(404, "Project not found")

    project.title = title[:160]
    project.category = category[:80]
    project.description = description
    project.location = location[:180] or None

    # Keep existing image if no new image is uploaded
    if image and image.filename:
        allowed_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }

        extension = Path(image.filename).suffix.lower()

        if extension not in allowed_types:
            raise HTTPException(400, "Only JPG, PNG and WEBP images are allowed.")

        if image.content_type != allowed_types[extension]:
            raise HTTPException(400, "Invalid image content type.")

        max_bytes = settings.max_upload_mb * 1024 * 1024
        content = await image.read(max_bytes + 1)

        if len(content) > max_bytes:
            raise HTTPException(400, "Image exceeds the upload size limit.")

        signatures = {
            ".jpg": content.startswith(b"\xff\xd8\xff"),
            ".jpeg": content.startswith(b"\xff\xd8\xff"),
            ".png": content.startswith(b"\x89PNG\r\n\x1a\n"),
            ".webp": (
                content.startswith(b"RIFF")
                and content[8:12] == b"WEBP"
            )
        }

        if not signatures[extension]:
            raise HTTPException(400, "Invalid image file.")

        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid4().hex}{extension}"
        (upload_dir / filename).write_bytes(content)

        project.image_path = (
            f"/{settings.upload_dir.replace(chr(92), '/')}/{filename}"
        )

    db.commit()

    return RedirectResponse("/admin#projects", status_code=303)


@router.post("/projects/{pid}/publish")
def publish_project(pid: int, request: Request, db: Session = Depends(get_db)):
    admin(request, db); p = db.get(Project, pid)
    if p: p.is_published = not p.is_published; db.commit()
    return RedirectResponse("/admin#projects", status_code=303)

@router.post("/projects/{pid}/delete")
def delete_project(pid: int, request: Request, db: Session = Depends(get_db)):
    admin(request, db); p = db.get(Project, pid)
    if p: db.delete(p); db.commit()
    return RedirectResponse("/admin#projects", status_code=303)
