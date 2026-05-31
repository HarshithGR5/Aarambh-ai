import qrcode
import uuid
import os
from io import BytesIO
from ..config import settings
import logging

logger = logging.getLogger(__name__)


def generate_child_qr(child_id: str) -> str:
    """Generate a QR code identifier for a child's Developmental Passport."""
    qr_id = f"AARAMBH-{child_id[:8].upper()}"
    return qr_id


def generate_qr_image(child_id: str, child_name: str) -> bytes:
    """Generate a QR code image (PNG bytes) for a child."""
    qr_data = f"aarambh://child/{child_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def save_qr_image(child_id: str, child_name: str) -> str:
    """Save QR code image to disk and return the file path."""
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"qr_{child_id}.png"
    filepath = os.path.join(upload_dir, filename)

    qr_bytes = generate_qr_image(child_id, child_name)
    with open(filepath, "wb") as f:
        f.write(qr_bytes)

    return f"/uploads/qr_{child_id}.png"
