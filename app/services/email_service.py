import logging
from app.config import settings
logger = logging.getLogger(__name__)

def send_enquiry_emails(enquiry):
    if not settings.resend_api_key:
        logger.warning("Email not sent: RESEND_API_KEY is not configured; enquiry %s is saved.", enquiry.reference)
        return False
    try:
        import resend
        resend.api_key = settings.resend_api_key
        body = f"New DynamicBuilds enquiry {enquiry.reference}\nName: {enquiry.customer_name}\nEmail: {enquiry.email}\nPhone: {enquiry.phone}\nService: {enquiry.service}\nLocation: {enquiry.location}\nProject: {enquiry.project_type}\nBudget: {enquiry.budget or 'Not provided'}\n\n{enquiry.description}"
        resend.Emails.send({"from": settings.email_from, "to": [settings.company_email], "subject": f"New project enquiry — {enquiry.reference}", "text": body})
        resend.Emails.send({"from": settings.email_from, "to": [enquiry.email], "subject": f"We received your enquiry — {enquiry.reference}", "text": f"Hello {enquiry.customer_name},\n\nThank you for contacting DynamicBuilds. Your enquiry reference is {enquiry.reference}. Our team will review your requirements.\n\nDynamicBuilds"})
        return True
    except Exception:
        logger.exception("Email delivery failed for enquiry %s", enquiry.reference)
        return False
