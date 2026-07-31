import logging
import asyncio
import os
import sys
from quart import Quart, jsonify, redirect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_HOST, APP_PORT, APP_DEBUG, SECRET_KEY
from services.database_service import DatabaseService
from services.captcha_service import CaptchaService
from services.system_service import SystemService
from routes.captcha_routes import setup_captcha_routes
from routes.api_routes import setup_api_routes
from routes.dashboard_routes import setup_dashboard_routes
from utils.helpers import setup_logging

logger = setup_logging("INFO")

app = Quart(__name__)
app.secret_key = SECRET_KEY

db_service: DatabaseService = None
captcha_service: CaptchaService = None
system_service: SystemService = None


@app.before_serving
async def startup():
    global db_service, captcha_service, system_service
    
    try:
        logger.info("=" * 50)
        logger.info("Starting CAPTCHA API")
        logger.info("=" * 50)
        logger.info("Initializing database connection...")
        db_service = DatabaseService()
        
        if not await db_service.connect():
            logger.error("Failed to connect to MongoDB")
            raise Exception("Database connection failed")
            
        await db_service.create_collections()
        
        logger.info("Initializing services...")
        captcha_service = CaptchaService(db_service.captcha_model)
        system_service = SystemService(db_service.system_stats_model)
        
        logger.info("Starting system monitoring...")
        await system_service.start_monitoring()
    
        logger.info("Setting up routes...")
        await setup_captcha_routes(app, captcha_service)
        await setup_api_routes(app, captcha_service, system_service)
        await setup_dashboard_routes(app)
    
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


@app.after_serving
async def shutdown():
    global system_service, db_service
    try:
        logger.info("Shutting down CAPTCHA API...")
        if system_service:
            await system_service.stop_monitoring()
        if db_service:
            await db_service.disconnect()
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

@app.errorhandler(404)
async def not_found(error):
    return jsonify({
        "success": False,
        "error": "Not found",
        "message": "The requested resource was not found"
    }), 404


@app.errorhandler(500)
async def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


@app.get("/")
async def index():
    return redirect("/dashboard")


if __name__ == "__main__":
    try:
        logger.info(f"Starting server on {APP_HOST}:{APP_PORT}")
        app.run(
            host=APP_HOST,
            port=APP_PORT,
            debug=APP_DEBUG
        )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
