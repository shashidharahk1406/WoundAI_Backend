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





# tasks.py
from celery import shared_task
from .models import WoundImage, WoundAnalysis
import os
from django.conf import settings

@shared_task
def run_ai_analysis_for_image(wound_image_id):
    return run_ai_analysis_for_image_sync(wound_image_id)

def run_ai_analysis_for_image_sync(wound_image_id):
    wi = WoundImage.objects.get(id=wound_image_id)
    img_path = wi.image.path if wi.image and hasattr(wi.image, 'path') else None
    # if using GCS, download file locally for inference
    if img_path is None:
        # download from storage
        from django.core.files.storage import default_storage
        local_tmp = f"/tmp/{os.path.basename(wi.image.name)}"
        with default_storage.open(wi.image.name, 'rb') as f:
            with open(local_tmp, 'wb') as out:
                out.write(f.read())
        img_path = local_tmp

    # Run tflite model inference (example)
    try:
        ai_out = run_tflite_inference(img_path)
    except Exception as e:
        ai_out = {"is_wound": False, "rejection_reason": f"AI failed: {e}"}

    # Map ai_out keys to WoundAnalysis fields
    allowed = {f.name for f in WoundAnalysis._meta.get_fields()}
    create_kwargs = {k: v for k, v in ai_out.items() if k in allowed}
    WoundAnalysis.objects.create(wound_image=wi, **create_kwargs)
    return True

# helper: tflite inference, adapt to your model input/output
def run_tflite_inference(image_path):
    # Example using tflite-runtime
    try:
        from tflite_runtime.interpreter import Interpreter
        import numpy as np
        from PIL import Image

        MODEL_PATH = '/app/model/wound_model.tflite'  # mount this in container
        interpreter = Interpreter(MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Preprocess: assume model takes 224x224 RGB normalized [0,1]
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224,224))
        input_arr = np.array(img).astype('float32') / 255.0
        input_arr = np.expand_dims(input_arr, axis=0)

        interpreter.set_tensor(input_details[0]['index'], input_arr)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        # Parse output_data to meaningful fields
        # This part depends on your model. Example:
        is_wound_score = float(output_data[0][0])
        is_wound = is_wound_score > 0.5
        # placeholder outputs
        return {
            "is_wound": is_wound,
            "rejection_reason": None if is_wound else "Low confidence",
            "wound_area_cm2": float(output_data[0][1]) if output_data.shape[1]>1 else None,
            # ... extend based on model outputs
        }
    except Exception as e:
        raise

