"""Création des QR Codes du musée avec logo central."""
import io

import qrcode
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from qrcode.constants import ERROR_CORRECT_H


def _logo_musee(size):
    """Charge le logo configuré ou crée un badge MNRDC de remplacement."""
    logo_path = getattr(settings, "MNRDC_QR_LOGO", None)
    if logo_path:
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Keep a white, opaque quiet zone behind transparent logo pixels so
            # the QR modules cannot show through and reduce the logo contrast.
            padding = max(3, size // 10)
            plate = Image.new("RGBA", (size, size), (255, 255, 255, 255))
            draw = ImageDraw.Draw(plate)
            draw.rounded_rectangle(
                (0, 0, size - 1, size - 1),
                radius=max(3, size // 8),
                fill=(255, 255, 255, 255),
                outline="#d1d5db",
                width=max(1, size // 48),
            )
            logo.thumbnail((size - 2 * padding, size - 2 * padding), Image.Resampling.LANCZOS)
            plate.alpha_composite(logo, ((size - logo.width) // 2, (size - logo.height) // 2))
            return plate
        except (OSError, TypeError):
            pass

    logo = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(logo)
    draw.rounded_rectangle((1, 1, size - 2, size - 2), radius=size // 5,
                           fill="#ffffff", outline="#163b32", width=max(2, size // 24))
    draw.ellipse((size // 6, size // 6, size * 5 // 6, size * 5 // 6), fill="#163b32")
    try:
        font = ImageFont.truetype("arial.ttf", size // 2)
    except OSError:
        font = ImageFont.load_default()
    text = "M"
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((size - (box[2] - box[0])) / 2, (size - (box[3] - box[1])) / 2 - box[1]),
              text, fill="#ffffff", font=font)
    return logo


def build_qr_png(value):
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H,
                       box_size=12, border=4)
    qr.add_data(value)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#163b32", back_color="white").convert("RGBA")
    logo_size = image.width // 5
    logo = _logo_musee(logo_size)
    image.alpha_composite(logo, ((image.width - logo.width) // 2,
                                 (image.height - logo.height) // 2))
    output = io.BytesIO()
    image.convert("RGB").save(output, format="PNG", optimize=True)
    return output.getvalue()
