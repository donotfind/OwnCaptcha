from datetime import datetime
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorCollection


class CaptchaModel:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create_captcha( self, captcha_id: str, answer: int, numbers: List[int] ) -> dict:
        document = {
            "captcha_id": captcha_id,
            "generated_at": datetime.utcnow(),
            "verified_at": None,
            "answer": answer,
            "user_answer": None,
            "is_correct": None,
            "numbers": numbers,
            "attempts": 0
        }
        
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document
    
    async def get_captcha(self, captcha_id: str) -> Optional[dict]:
        return await self.collection.find_one({"captcha_id": captcha_id})
    
    async def verify_captcha(self, captcha_id: str, user_answer: int ) -> Optional[bool]:
        captcha = await self.get_captcha(captcha_id)

        if not captcha:
            return None
        
        is_correct = user_answer == captcha["answer"]

        await self.collection.update_one(
            {"captcha_id": captcha_id},
            {
                "$set": {
                    "verified_at": datetime.utcnow(),
                    "user_answer": user_answer,
                    "is_correct": is_correct
                },
                "$inc": {"attempts": 1}
            }
        )
        
        return is_correct
    
    async def get_total_generated(self) -> int:
        return await self.collection.count_documents({})
    
    async def get_total_verified(self) -> int:
        return await self.collection.count_documents({"verified_at": {"$ne": None}})
    
    async def get_total_correct(self) -> int:
        return await self.collection.count_documents({"is_correct": True})
    
    async def get_generated_in_hours(self, hours: int = 24) -> int:
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours) 
        return await self.collection.count_documents({
            "generated_at": {"$gt": cutoff_time}
        })
    
    async def get_verified_in_hours(self, hours: int = 24) -> int:
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return await self.collection.count_documents({
            "verified_at": {"$gt": cutoff_time, "$ne": None}
        })

    async def get_correct_in_hours(self, hours: int = 24) -> int:
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return await self.collection.count_documents({
            "is_correct": True,
            "verified_at": {"$gt": cutoff_time, "$ne": None}
        })
    
    async def get_time_based_stats(self) -> dict:
        """Get verified and correct counts for multiple time periods."""
        periods = [1, 2, 6, 12, 24]
        stats = {}
        for hours in periods:
            stats[f"last_{hours}h"] = {
                "verified": await self.get_verified_in_hours(hours),
                "correct": await self.get_correct_in_hours(hours),
            }
        return stats
    
    async def get_accuracy_rate(self) -> float:
        total_verified = await self.get_total_verified()
        if total_verified == 0:
            return 0.0
        total_correct = await self.get_total_correct()
        return round((total_correct / total_verified) * 100, 2)
    
    async def get_statistics(self) -> dict:
        total_generated = await self.get_total_generated()
        total_verified = await self.get_total_verified()
        total_correct = await self.get_total_correct()
        accuracy_rate = await self.get_accuracy_rate()
        generated_last_hour = await self.get_generated_in_hours(1)
        generated_last_24h = await self.get_generated_in_hours(24)
        verified_last_hour = await self.get_verified_in_hours(1)
        verified_last_24h = await self.get_verified_in_hours(24)
        correct_last_hour = await self.get_correct_in_hours(1)
        correct_last_24h = await self.get_correct_in_hours(24)
        time_based_stats = await self.get_time_based_stats()
        
        return {
            "total_generated": total_generated,
            "total_verified": total_verified,
            "total_correct": total_correct,
            "accuracy_rate": accuracy_rate,
            "generated_last_hour": generated_last_hour,
            "generated_last_24h": generated_last_24h,
            "verified_last_hour": verified_last_hour,
            "verified_last_24h": verified_last_24h,
            "correct_last_hour": correct_last_hour,
            "correct_last_24h": correct_last_24h,
            "time_based_stats": time_based_stats,
        }
    
    async def cleanup_old_records(self, days: int = 2) -> int:
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        result = await self.collection.delete_many({
            "generated_at": {"$lt": cutoff_time}
        })
        return result.deleted_count

    async def get_recent_captchas(self, limit: int = 50) -> List[dict]:
        cursor = self.collection.find({}).sort("generated_at", -1).limit(limit)
        recent = []
        async for doc in cursor:
            doc_id = str(doc.get("_id", ""))
            generated_at = doc.get("generated_at")
            verified_at = doc.get("verified_at")
            recent.append({
                "captcha_id": doc.get("captcha_id"),
                "generated_at": generated_at.isoformat() if isinstance(generated_at, datetime) else generated_at,
                "verified_at": verified_at.isoformat() if isinstance(verified_at, datetime) else verified_at,
                "answer": doc.get("answer"),
                "user_answer": doc.get("user_answer"),
                "is_correct": doc.get("is_correct"),
                "attempts": doc.get("attempts", 0)
            })
        return recent
