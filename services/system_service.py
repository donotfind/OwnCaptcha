"""
System Monitoring Service
"""
import logging
import asyncio
import psutil
from typing import Optional
from models.system_stats_model import SystemStatsModel
from config.settings import SYSTEM_STATS_INTERVAL

logger = logging.getLogger(__name__)


class SystemService:
    """Service for monitoring system resources."""
    
    def __init__(self, system_stats_model: SystemStatsModel):
        """
        Initialize system service.
        
        Args:
            system_stats_model: SystemStatsModel instance
        """
        self.model = system_stats_model
        self.interval = SYSTEM_STATS_INTERVAL
        self._monitoring = False
        self._monitor_task = None
    
    def get_cpu_stats(self) -> dict:
        """
        Get current CPU statistics.
        
        Returns:
            Dictionary with CPU stats
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "cpu_freq_current": cpu_freq.current if cpu_freq else 0,
                "cpu_freq_max": cpu_freq.max if cpu_freq else 0,
            }
        
        except Exception as e:
            logger.error(f"Error getting CPU stats: {e}")
            return {"cpu_percent": 0, "cpu_count": 0}
    
    def get_memory_stats(self) -> dict:
        """
        Get current memory statistics.
        
        Returns:
            Dictionary with memory stats
        """
        try:
            memory = psutil.virtual_memory()
            
            return {
                "memory_percent": memory.percent,
                "memory_used_mb": round(memory.used / (1024 * 1024), 2),
                "memory_available_mb": round(memory.available / (1024 * 1024), 2),
                "memory_total_mb": round(memory.total / (1024 * 1024), 2),
                "memory_free_mb": round(memory.free / (1024 * 1024), 2),
            }
        
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"memory_percent": 0}
    
    def get_disk_stats(self, path: str = "/") -> dict:
        """
        Get disk statistics.
        
        Args:
            path: Path to check disk usage
        
        Returns:
            Dictionary with disk stats
        """
        try:
            disk = psutil.disk_usage(path)
            
            return {
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
                "disk_total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "disk_free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
            }
        
        except Exception as e:
            logger.error(f"Error getting disk stats: {e}")
            return {"disk_percent": 0}
    
    def get_all_stats(self) -> dict:
        """
        Get all system statistics.
        
        Returns:
            Dictionary with all system stats
        """
        cpu_stats = self.get_cpu_stats()
        memory_stats = self.get_memory_stats()
        disk_stats = self.get_disk_stats()
        
        return {
            **cpu_stats,
            **memory_stats,
            **disk_stats,
        }
    
    async def record_stats(self):
        """
        Record current system statistics to database.
        
        Returns:
            Recorded stats document or None
        """
        try:
            stats = self.get_all_stats()
            
            recorded = await self.model.record_stats(
                cpu_percent=stats.get("cpu_percent", 0),
                memory_percent=stats.get("memory_percent", 0),
                disk_percent=stats.get("disk_percent", 0),
                memory_used_mb=stats.get("memory_used_mb", 0),
                memory_available_mb=stats.get("memory_available_mb", 0),
                memory_total_mb=stats.get("memory_total_mb", 0),
                disk_used_gb=stats.get("disk_used_gb", 0),
                disk_total_gb=stats.get("disk_total_gb", 0),
                disk_free_gb=stats.get("disk_free_gb", 0),
            )
            
            logger.debug(f"Recorded system stats: {recorded}")
            return recorded
        
        except Exception as e:
            logger.error(f"Error recording stats: {e}")
            return None
    
    async def start_monitoring(self):
        """Start background monitoring task."""
        if self._monitoring:
            logger.warning("Monitoring already started")
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("System monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring task."""
        if not self._monitoring:
            logger.warning("Monitoring not running")
            return
        
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("System monitoring stopped")
    
    async def _monitor_loop(self):
        """Background monitoring loop."""
        try:
            while self._monitoring:
                await self.record_stats()
                await asyncio.sleep(self.interval)
        
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
    
    async def get_statistics(self) -> dict:
        """
        Get system statistics summary.
        
        Returns:
            Dictionary with current stats and averages
        """
        try:
            current_stats = self.get_all_stats()
            
            # Get averages for last 24 hours
            cpu_avg = await self.model.get_cpu_average(hours=24)
            memory_avg = await self.model.get_memory_average(hours=24)
            disk_avg = await self.model.get_disk_average(hours=24)
            peak_stats = await self.model.get_peak_stats(hours=24)
            
            return {
                "current": current_stats,
                "averages_24h": {
                    "cpu": cpu_avg,
                    "memory": memory_avg,
                    "disk": disk_avg,
                },
                "peak_24h": peak_stats,
            }
        
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"current": {}}
    
    async def cleanup_old_records(self, days: int = 7) -> int:
        """
        Clean up old records.
        
        Args:
            days: Days to retain
        
        Returns:
            Number of deleted records
        """
        try:
            deleted = await self.model.cleanup_old_records(days=days)
            logger.info(f"Cleaned up {deleted} old system records")
            return deleted
        
        except Exception as e:
            logger.error(f"Error cleaning up records: {e}")
            return 0
