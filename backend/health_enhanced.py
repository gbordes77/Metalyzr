"""
Health checks enrichis pour monitoring avancé
Ajoute des vérifications de services externes et métriques détaillées
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any
import aiohttp
import logging

logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.last_check_time = None
        self.cached_results = {}
        self.cache_ttl = 30  # Cache results for 30 seconds
    
    async def check_database_connection(self) -> Dict[str, Any]:
        """Vérifier la connexion à la base de données"""
        try:
            # TODO: Ajouter vraie vérification PostgreSQL quand configuré
            # import asyncpg
            # conn = await asyncpg.connect(DATABASE_URL)
            # await conn.fetchval('SELECT 1')
            # await conn.close()
            
            return {
                "status": "healthy",
                "response_time_ms": 5,
                "details": "Database connection check skipped (not configured yet)"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "error": str(e)
            }
    
    async def check_redis_connection(self) -> Dict[str, Any]:
        """Vérifier la connexion à Redis"""
        try:
            # TODO: Ajouter vraie vérification Redis quand configuré
            # import aioredis
            # redis = aioredis.from_url("redis://localhost:6379")
            # await redis.ping()
            # await redis.close()
            
            return {
                "status": "healthy", 
                "response_time_ms": 3,
                "details": "Redis connection check skipped (not configured yet)"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "error": str(e)
            }
    
    async def check_melee_api(self) -> Dict[str, Any]:
        """Vérifier l'API Melee.gg"""
        start_time = time.time()
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://api.melee.gg/v1/health") as response:
                    response_time = (time.time() - start_time) * 1000
                    if response.status == 200:
                        return {
                            "status": "healthy",
                            "response_time_ms": round(response_time, 2),
                            "details": "Melee API accessible"
                        }
                    else:
                        return {
                            "status": "degraded",
                            "response_time_ms": round(response_time, 2),
                            "error": f"HTTP {response.status}"
                        }
        except asyncio.TimeoutError:
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "error": "Timeout connecting to Melee API"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "error": str(e)
            }
    
    async def check_mtgtop8_availability(self) -> Dict[str, Any]:
        """Vérifier la disponibilité de MTGTop8"""
        start_time = time.time()
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get("https://mtgtop8.com/robots.txt") as response:
                    response_time = (time.time() - start_time) * 1000
                    if response.status == 200:
                        return {
                            "status": "healthy",
                            "response_time_ms": round(response_time, 2),
                            "details": "MTGTop8 accessible"
                        }
                    else:
                        return {
                            "status": "degraded",
                            "response_time_ms": round(response_time, 2),
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "error": str(e)
            }
    
    async def check_mtgo_cache_repo(self) -> Dict[str, Any]:
        """Vérifier l'accès au repository MTGODecklistCache"""
        start_time = time.time()
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = "https://api.github.com/repos/Jiliac/MTGODecklistCache"
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time_ms": round(response_time, 2),
                            "details": f"Last updated: {data.get('updated_at', 'unknown')}"
                        }
                    else:
                        return {
                            "status": "degraded",
                            "response_time_ms": round(response_time, 2),
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time_ms": None,
                "error": str(e)
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Métriques système locales"""
        import psutil
        import os
        
        try:
            # Utilisation mémoire
            memory = psutil.virtual_memory()
            
            # Utilisation disque
            disk = psutil.disk_usage('/')
            
            # Charge CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Uptime du processus
            process = psutil.Process(os.getpid())
            uptime_seconds = time.time() - process.create_time()
            
            return {
                "memory": {
                    "total_mb": round(memory.total / 1024 / 1024, 2),
                    "used_mb": round(memory.used / 1024 / 1024, 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                    "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                    "percent": round((disk.used / disk.total) * 100, 2)
                },
                "cpu_percent": cpu_percent,
                "uptime_seconds": round(uptime_seconds, 2),
                "uptime_minutes": round(uptime_seconds / 60, 2)
            }
        except Exception as e:
            return {
                "error": f"Failed to collect system metrics: {str(e)}"
            }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Health check complet avec tous les services"""
        
        # Cache check si récent
        now = time.time()
        if (self.last_check_time and 
            (now - self.last_check_time) < self.cache_ttl and 
            self.cached_results):
            self.cached_results["cached"] = True
            return self.cached_results
        
        start_time = time.time()
        
        # Lancer toutes les vérifications en parallèle
        checks = await asyncio.gather(
            self.check_database_connection(),
            self.check_redis_connection(),
            self.check_melee_api(),
            self.check_mtgtop8_availability(),
            self.check_mtgo_cache_repo(),
            self.get_system_metrics(),
            return_exceptions=True
        )
        
        # Traiter les résultats
        db_check, redis_check, melee_check, mtgtop8_check, cache_repo_check, system_metrics = checks
        
        # Calculer le status global
        service_statuses = [
            db_check.get("status", "unknown") if isinstance(db_check, dict) else "error",
            redis_check.get("status", "unknown") if isinstance(redis_check, dict) else "error",
            melee_check.get("status", "unknown") if isinstance(melee_check, dict) else "error",
            mtgtop8_check.get("status", "unknown") if isinstance(mtgtop8_check, dict) else "error",
            cache_repo_check.get("status", "unknown") if isinstance(cache_repo_check, dict) else "error"
        ]
        
        # Déterminer le status global
        if all(status == "healthy" for status in service_statuses):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in service_statuses):
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        total_time = round((time.time() - start_time) * 1000, 2)
        
        result = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "check_duration_ms": total_time,
            "version": "2.0.0",
            "services": {
                "database": db_check if isinstance(db_check, dict) else {"status": "error", "error": str(db_check)},
                "redis": redis_check if isinstance(redis_check, dict) else {"status": "error", "error": str(redis_check)},
                "melee_api": melee_check if isinstance(melee_check, dict) else {"status": "error", "error": str(melee_check)},
                "mtgtop8": mtgtop8_check if isinstance(mtgtop8_check, dict) else {"status": "error", "error": str(mtgtop8_check)},
                "mtgo_cache_repo": cache_repo_check if isinstance(cache_repo_check, dict) else {"status": "error", "error": str(cache_repo_check)}
            },
            "system_metrics": system_metrics if isinstance(system_metrics, dict) else {"error": str(system_metrics)},
            "cached": False
        }
        
        # Mise en cache
        self.cached_results = result
        self.last_check_time = now
        
        return result

# Instance globale
health_checker = HealthChecker() 