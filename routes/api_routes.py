import logging
from quart import Blueprint, jsonify, session
from services.captcha_service import CaptchaService
from services.system_service import SystemService

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


async def setup_api_routes( app, captcha_service: CaptchaService, system_service: SystemService ):
    @api_bp.get("/stats")
    async def get_captcha_stats():
        """Get CAPTCHA statistics."""
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        try:
            stats = await captcha_service.get_statistics()
            return jsonify(stats)
        
        except Exception as e:
            logger.error(f"Error getting CAPTCHA stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    @api_bp.get("/system/stats")
    async def get_system_stats():
        """Get current system statistics."""
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        try:
            stats = system_service.get_all_stats()
            return jsonify(stats)
        
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    @api_bp.get("/system/history")
    async def get_system_history():
        """Get system statistics history."""
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        try:
            hours = 24
            history = await system_service.model.get_stats_history(hours=hours)
            
            # Convert to JSON-serializable format
            history_data = []
            for record in history:
                record["_id"] = str(record.get("_id", ""))
                record["timestamp"] = record["timestamp"].isoformat()
                history_data.append(record)
            
            return jsonify({"data": history_data})
        
        except Exception as e:
            logger.error(f"Error getting system history: {e}")
            return jsonify({"error": str(e)}), 500
    
    @api_bp.get("/system/summary")
    async def get_system_summary():
        """Get system statistics summary."""
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        try:
            summary = await system_service.get_statistics()
            return jsonify(summary)
        
        except Exception as e:
            logger.error(f"Error getting system summary: {e}")
            return jsonify({"error": str(e)}), 500

    @api_bp.get("/admin/recent")
    async def get_recent_captchas():
        """Get recent CAPTCHAs log."""
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        try:
            recent = await captcha_service.get_recent_captchas(limit=50)
            return jsonify({"success": True, "data": recent})

        except Exception as e:
            logger.error(f"Error getting recent captchas: {e}")
            return jsonify({"error": str(e)}), 500
    
    @api_bp.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            return jsonify({
                "status": "OK",
                "service": "CAPTCHA API"
            })

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({"status": "ERROR", "error": str(e)}), 500

    @api_bp.get("/stats/time-based")
    async def get_time_based_stats():
        """Get CAPTCHA statistics for multiple time periods (1h, 2h, 6h, 12h, 24h)."""
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized"}), 401
        try:
            stats = await captcha_service.get_statistics()
            time_based = stats.get("time_based_stats", {})
            
            # Format for easier frontend consumption
            formatted = {}
            for period, data in time_based.items():
                hours = int(period.replace("last_", "").replace("h", ""))
                formatted[f"{hours}h"] = {
                    "verified": data.get("verified", 0),
                    "correct": data.get("correct", 0),
                    "accuracy": round((data.get("correct", 0) / data.get("verified", 1)) * 100, 1) if data.get("verified", 0) > 0 else 0
                }
            
            return jsonify({
                "success": True,
                "data": formatted,
                "summary": {
                    "total_generated": stats.get("total_generated", 0),
                    "total_verified": stats.get("total_verified", 0),
                    "total_correct": stats.get("total_correct", 0),
                    "overall_accuracy": stats.get("accuracy_rate", 0)
                }
            })
        
        except Exception as e:
            logger.error(f"Error getting time-based stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    app.register_blueprint(api_bp)
