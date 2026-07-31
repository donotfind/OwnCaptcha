import logging
import os
from io import BytesIO

from quart import Blueprint, jsonify, send_file

from services.captcha_service import CaptchaService

logger = logging.getLogger(__name__)

captcha_bp = Blueprint("captcha", __name__, url_prefix="/api")


async def setup_captcha_routes(app, captcha_service: CaptchaService):
    @captcha_bp.get("/captcha")
    async def generate_captcha():
        """Generate a new CAPTCHA."""
        try:
            captcha_id, answer, numbers = await captcha_service.generate_captcha()

            return jsonify(
                {
                    "success": True,
                    "captcha_id": captcha_id,
                    "image": f"/api/images/{captcha_id}.png",
                    "numbers": numbers,
                }
            )

        except Exception as e:
            logger.exception("Error generating CAPTCHA")
            return jsonify({"success": False, "error": str(e)}), 500

    @captcha_bp.post("/verify/<captcha_id>/<int:user_answer>")
    async def verify_captcha(captcha_id: str, user_answer: int):
        """Verify CAPTCHA answer."""
        try:
            is_correct = await captcha_service.verify_captcha(
                captcha_id, user_answer
            )

            if is_correct is None:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "CAPTCHA not found",
                        }
                    ),
                    404,
                )

            return jsonify(
                {
                    "success": True,
                    "correct": is_correct,
                    "message": "Correct! ✓" if is_correct else "Incorrect ✗",
                }
            )

        except Exception as e:
            logger.exception("Error verifying CAPTCHA")
            return jsonify({"success": False, "error": str(e)}), 500

    @captcha_bp.get("/images/<captcha_id>.png")
    async def get_image(captcha_id: str):
        """Serve CAPTCHA image and delete it immediately afterwards."""
        try:
            filepath = os.path.join("captchas", f"{captcha_id}.png")

            if not os.path.isfile(filepath):
                return jsonify({"success": False, "error": "Image not found"}), 404

            # Read image into memory
            with open(filepath, "rb") as f:
                image_bytes = f.read()

            # Delete file immediately
            try:
                os.remove(filepath)
                logger.info("Deleted CAPTCHA image: %s", filepath)
            except Exception as ex:
                logger.warning("Failed to delete %s: %s", filepath, ex)

            # Send image from memory
            return await send_file(
                BytesIO(image_bytes),
                mimetype="image/png",
            )

        except Exception as e:
            logger.exception("Error serving CAPTCHA image")
            return jsonify({"success": False, "error": str(e)}), 500

    app.register_blueprint(captcha_bp)
