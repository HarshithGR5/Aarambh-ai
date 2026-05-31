import os
from io import BytesIO
from ..config import settings
import logging

logger = logging.getLogger(__name__)


def generate_referral_pdf(
    referral_id: str,
    child_name: str,
    letter_text: str,
    facility_name: str = "",
) -> bytes:
    """Generate a PDF referral letter and return bytes."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
        styles = getSampleStyleSheet()

        story = []
        title = Paragraph("AARAMBH AI — Developmental Referral Letter", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 0.5 * cm))

        subtitle = Paragraph(f"Child: {child_name}", styles["Heading2"])
        story.append(subtitle)
        story.append(Spacer(1, 0.5 * cm))

        for line in letter_text.split("\n"):
            if line.strip():
                p = Paragraph(line, styles["Normal"])
                story.append(p)
                story.append(Spacer(1, 0.2 * cm))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        logger.warning("reportlab not available, returning plain text PDF placeholder")
        return letter_text.encode("utf-8")


def save_referral_pdf(referral_id: str, child_name: str, letter_text: str) -> str:
    """Save referral PDF and return file path."""
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"referral_{referral_id}.pdf"
    filepath = os.path.join(upload_dir, filename)

    pdf_bytes = generate_referral_pdf(referral_id, child_name, letter_text)
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)

    return f"/uploads/{filename}"
