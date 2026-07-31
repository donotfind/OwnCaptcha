from datetime import datetime, timedelta
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorCollection


class SystemStatsModel:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def record_stats(
        self,
        cpu_percent: float,
        memory_percent: float,
        disk_percent: float,
        memory_used_mb: float,
        memory_available_mb: float,
        memory_total_mb: float,
        disk_used_gb: float,
        disk_total_gb: float,
        disk_free_gb: float
    ) -> dict:
        document = {
            "timestamp": datetime.utcnow(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "memory_used_mb": memory_used_mb,
            "memory_available_mb": memory_available_mb,
            "memory_total_mb": memory_total_mb,
            "disk_used_gb": disk_used_gb,
            "disk_total_gb": disk_total_gb,
            "disk_free_gb": disk_free_gb
        }
        
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document
    
    async def get_current_stats(self) -> Optional[dict]:
        return await self.collection.find_one(
            sort=[("timestamp", -1)]
        )
    
    async def get_stats_history(self, hours: int = 24) -> List[dict]:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cursor = self.collection.find({
            "timestamp": {"$gt": cutoff_time}
        }).sort("timestamp", 1)
        
        return await cursor.to_list(length=None)
    
    async def get_cpu_average(self, hours: int = 24) -> float:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gt": cutoff_time}}},
            {"$group": {"_id": None, "average": {"$avg": "$cpu_percent"}}}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["average"] if result else 0.0
    
    async def get_memory_average(self, hours: int = 24) -> float:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gt": cutoff_time}}},
            {"$group": {"_id": None, "average": {"$avg": "$memory_percent"}}}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["average"] if result else 0.0
    
    async def get_disk_average(self, hours: int = 24) -> float:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gt": cutoff_time}}},
            {"$group": {"_id": None, "average": {"$avg": "$disk_percent"}}}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["average"] if result else 0.0
    
    async def get_peak_stats(self, hours: int = 24) -> dict:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gt": cutoff_time}}},
            {
                "$group": {
                    "_id": None,
                    "peak_cpu": {"$max": "$cpu_percent"},
                    "peak_memory": {"$max": "$memory_percent"},
                    "peak_disk": {"$max": "$disk_percent"}
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        
        if result:
            return {
                "peak_cpu": result[0]["peak_cpu"],
                "peak_memory": result[0]["peak_memory"],
                "peak_disk": result[0]["peak_disk"]
            }
        
        return {"peak_cpu": 0, "peak_memory": 0, "peak_disk": 0}
    
    async def cleanup_old_records(self, days: int = 1) -> int:
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        result = await self.collection.delete_many({
            "timestamp": {"$lt": cutoff_time}
        })
        
        return result.deleted_count
