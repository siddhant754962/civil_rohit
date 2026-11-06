from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import uuid4
from app.database import get_db
from app.models import Enquiry, Project, Service
from app.services.email_service import send_enquiry_emails
from app.services.upload_service import save_upload
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")
SERVICES = [
("Building Layout Planning", "Functional floor plans and thoughtful space planning shaped around your requirements."),
("Building Renovation", "Practical renovation concepts for improving existing spaces, interiors and exteriors."),
("Interior and Exterior Design", "Interior concepts, facade ideas, finishes and space-conscious design guidance."),
("STAAD.Pro Structural Analysis", "Structural modelling and analysis workflows with engineering documentation."),
("Construction Estimation", "Quantity calculations, preliminary budgets and BOQ documentation where offered.")]

def page(request, name, **kwargs):
    return templates.TemplateResponse(request=request, name=name, context={"request": request, "company_email": settings.company_email, "company_phone": settings.company_phone, **kwargs})

@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    projects = db.scalars(select(Project).where(Project.is_published == True).order_by(Project.created_at.desc()).limit(3)).all()
    return page(request, "index.html", projects=projects, services=SERVICES)

@router.get("/about")
def about(request: Request):
    return page(request, "about.html")

@router.get("/services")
def services(request: Request): return page(request, "services.html", services=SERVICES)

@router.get("/projects")
def projects(request: Request, db: Session = Depends(get_db)):
    items = db.scalars(select(Project).where(Project.is_published == True).order_by(Project.created_at.desc())).all()
    return page(request, "projects.html", projects=items)

@router.get("/contact")
def contact(request: Request):
    selected_service = request.query_params.get("service", "")
    return page(request, "contact.html", services=[s[0] for s in SERVICES], selected_service=selected_service)

@router.post("/enquiries")
async def create_enquiry(request: Request, name: str = Form(...), email: str = Form(...), phone: str = Form(...), service: str = Form(...), location: str = Form(...), project_type: str = Form(...), description: str = Form(...), budget: str = Form(""), preferred_contact: str = Form("Email"), attachment: UploadFile | None = File(None), website: str = Form(""), db: Session = Depends(get_db)):
    if website: raise HTTPException(400, "Invalid submission.")
    name, email, phone, description = name.strip(), email.strip().lower(), phone.strip(), description.strip()
    if len(name) < 2 or len(name) > 120 or "@" not in email or len(phone) < 7 or len(phone) > 30 or len(description) < 15:
        raise HTTPException(422, "Please provide valid contact details and a project description of at least 15 characters.")
    allowed_services = {s[0] for s in SERVICES}
    if service not in allowed_services: raise HTTPException(422, "Please select a valid service.")
    path = await save_upload(attachment)
    item = Enquiry(reference=f"DB-{uuid4().hex[:8].upper()}", customer_name=name, email=email, phone=phone, service=service, location=location.strip()[:180], project_type=project_type.strip()[:100], budget=budget.strip()[:80] or None, description=description, attachment_path=path, preferred_contact=preferred_contact)
    db.add(item); db.commit(); db.refresh(item)
    send_enquiry_emails(item)
    return page(request, "success.html", reference=item.reference)

@router.get("/privacy")
def privacy(request: Request): return page(request, "legal.html", heading="Privacy Policy", content="We use the information you submit only to respond to your project enquiry and manage communications. Enquiries are stored securely for business follow-up. Contact us to request access or correction.")

@router.get("/terms")
def terms(request: Request): return page(request, "legal.html", heading="Terms and Conditions", content="Website information is general and does not constitute construction, structural or legal approval. Project scope, fees, deliverables and professional responsibilities must be agreed in writing before work begins. All structural recommendations must be reviewed and approved by appropriately qualified professionals before construction.")

@router.get("/robots.txt")
def robots():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: " + settings.base_url.rstrip("/") + "/sitemap.xml")

@router.get("/sitemap.xml")
def sitemap():
    from fastapi.responses import Response
    base = settings.base_url.rstrip("/")
    urls = "".join(f"<url><loc>{base}{p}</loc></url>" for p in ["/", "/about", "/services", "/projects", "/contact", "/privacy", "/terms"])
    return Response(f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>{urls}</urlset>", media_type="application/xml")
