"""
Database Service for MongoDB async operations
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config.settings import MONGODB_URL, MONGODB_DB_NAME, COLLECTIONS
from models.captcha_model import CaptchaModel
from models.system_stats_model import SystemStatsModel

logger = logging.getLogger(__name__)


class DatabaseService:
    """Manages MongoDB connections and models."""
    
    def __init__(self):
        """Initialize database service."""
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
        self.captcha_model: CaptchaModel = None
        self.system_stats_model: SystemStatsModel = None
    
    async def connect(self) -> bool:
        """
        Connect to MongoDB.
        
        Returns:
            True if connection successful
        """
        try:
            logger.info(f"Connecting to MongoDB")
            self.client = AsyncIOMotorClient(MONGODB_URL)
            self.db = self.client[MONGODB_DB_NAME]
            
            # Verify connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Initialize models
            await self._init_models()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _init_models(self):
        """Initialize database models."""
        try:
            # Create indexes
            captcha_collection = self.db[COLLECTIONS["captcha_stats"]]
            system_collection = self.db[COLLECTIONS["system_stats"]]
            
            # Create unique index on captcha_id
            await captcha_collection.create_index("captcha_id", unique=True)
            
            # Create TTL index on timestamp for auto-cleanup
            await system_collection.create_index(
                "timestamp",
                expireAfterSeconds=7*24*60*60  # 7 days
            )
            
            # Initialize models
            self.captcha_model = CaptchaModel(captcha_collection)
            self.system_stats_model = SystemStatsModel(system_collection)
            
            logger.info("Database models initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise
    
    async def create_collections(self):
        """Create database collections if they don't exist."""
        try:
            existing_collections = await self.db.list_collection_names()
            
            for collection_name in COLLECTIONS.values():
                if collection_name not in existing_collections:
                    await self.db.create_collection(collection_name)
                    logger.info(f"Created collection: {collection_name}")
        
        except Exception as e:
            logger.error(f"Failed to create collections: {e}")
            raise
    
    async def drop_database(self):
        """Drop entire database (use with caution)."""
        try:
            if self.client:
                await self.client.drop_database(MONGODB_DB_NAME)
                logger.warning("Database dropped")
        
        except Exception as e:
            logger.error(f"Failed to drop database: {e}")
    
    async def get_db_stats(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database stats
        """
        try:
            stats = await self.db.command("dbStats")
            return {
                "db_name": stats.get("db"),
                "collections": stats.get("collections", 0),
                "data_size_mb": round(stats.get("dataSize", 0) / (1024 * 1024), 2),
                "index_size_mb": round(stats.get("indexSize", 0) / (1024 * 1024), 2),
                "storage_size_mb": round(stats.get("storageSize", 0) / (1024 * 1024), 2),
            }
        
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """
        Check database health.
        
        Returns:
            True if database is healthy
        """
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
            return False
        
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
