from celery import shared_task
import google.generativeai as genai
from django.conf import settings
from .models import Prescription, AuditLog, Report

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_prescription_ai_task(self, prescription_id):
    try:
        pres = Prescription.objects.get(id=prescription_id)
    except Prescription.DoesNotExist:
        return

    patient = pres.patient
    wound = pres.wound

    prompt = f"""
    You are a wound-care AI assistant.
    Generate a treatment prescription for the following patient:

    Patient:
      - Name: {patient.name}
      - Age: {patient.age}
      - Gender: {patient.gender}
      - Comorbidities: {patient.comorbidities}

    Wound:
      - Type: {wound.wound_type if wound else "N/A"}
      - Location: {wound.wound_location if wound else "N/A"}
      - Notes: {wound.notes if wound else ""}

    Return a structured JSON with fields:
      - diagnosis
      - medications (list)
      - dressing_recommendation
      - follow_up_in_days
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        ai_result = response.text.strip()

        pres.ai_suggestion = {"suggestion": ai_result}
        pres.model_version = "gemini-1.5-flash"
        pres.status = "ai_generated"
        pres.save()

        AuditLog.objects.create(
            user=None,
            action="ai_generated",
            object_type="Prescription",
            object_id=str(pres.id),
            details={"model": "gemini-1.5-flash"}
        )

    except Exception as exc:
        pres.status = "pending"
        pres.save()
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_report_ai_task(self, report_id):
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return

    patient = report.patient

    prompt = f"""
    You are a medical AI assistant.
    Generate a wound progress report for the patient:

    Patient:
      - Name: {patient.name}
      - Age: {patient.age}
      - Gender: {patient.gender}
      - Comorbidities: {patient.comorbidities}

    Report Title: {report.title}
    Description: {report.description}

    Return a structured JSON with fields:
      - summary
      - wound_progress
      - risk_factors
      - recommendations
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        ai_result = response.text.strip()

        report.description = f"{report.description}\n\nAI Summary:\n{ai_result}"
        report.status = "uploaded"
        report.save()

        AuditLog.objects.create(
            user=None,
            action="ai_report_generated",
            object_type="Report",
            object_id=str(report.id),
            details={"model": "gemini-1.5-flash"}
        )

    except Exception as exc:
        self.retry(exc=exc)
