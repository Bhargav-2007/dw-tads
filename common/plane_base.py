"""Base plane runner application for DW-TADS planes.
Orchestrates microservices within a plane and provides plane-level HTTP endpoints.
"""
import asyncio
import os
import signal
import socket
from typing import List, Type
try:
    from aiohttp import web
except ImportError:
    web = None

from common.base_service import BaseService, utc_now


class PlaneRunner:
    """Runs all microservices assigned to a plane and exposes plane endpoints."""

    def __init__(self, plane_id: int, plane_name: str, plane_port: int, service_classes: List[Type[BaseService]]):
        self.plane_id = plane_id
        self.plane_name = plane_name
        self.plane_port = plane_port
        self.service_classes = service_classes
        self.services: List[BaseService] = []
        self.service_tasks: List[asyncio.Task] = []
        self._app: web.Application = web.Application()
        self._runner: web.AppRunner = None
        self._site: web.TCPSite = None
        self.running = False

    def _setup_routes(self):
        self._app.router.add_get("/services", self._services_handler)
        self._app.router.add_get("/health", self._health_handler)
        self._app.router.add_get("/ready", self._ready_handler)
        self._app.router.add_get("/metrics", self._metrics_handler)

    async def _services_handler(self, request: web.Request) -> web.Response:
        """GET /services — list every service in the plane."""
        service_list = []
        for s in self.services:
            h = await s.health()
            service_list.append({
                "name": s.NAME,
                "plane": s.PLANE,
                "tier": s.TIER,
                "input_topics": s.INPUT_TOPICS,
                "output_topics": s.OUTPUT_TOPICS,
                "http_port": s.HTTP_PORT,
                "health": h,
            })
        return web.json_response({
            "plane": self.plane_id,
            "name": self.plane_name,
            "count": len(self.services),
            "services": service_list,
        })

    async def _health_handler(self, request: web.Request) -> web.Response:
        """GET /health — returns overall plane health."""
        return web.json_response({
            "status": "ok",
            "plane": self.plane_id,
            "plane_name": self.plane_name,
            "services_count": len(self.services),
            "timestamp": utc_now(),
        })

    def _check_tcp(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """Check TCP socket connectivity."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except Exception:
            return False

    async def _ready_handler(self, request: web.Request) -> web.Response:
        """GET /ready — returns 200 only when Kafka, Postgres, Neo4j are reachable."""
        kafka_host = os.getenv("KAFKA_HOST", "kafka" if os.getenv("DOCKER_CONTAINER") else "localhost")
        kafka_port = int(os.getenv("KAFKA_PORT", "9092"))
        pg_host = os.getenv("PGHOST", "postgres" if os.getenv("DOCKER_CONTAINER") else "localhost")
        pg_port = int(os.getenv("PGPORT", "5432"))
        neo_host = os.getenv("NEO4J_HOST", "neo4j" if os.getenv("DOCKER_CONTAINER") else "localhost")
        neo_port = int(os.getenv("NEO4J_BOLT_PORT", "7687"))

        kafka_ok = await asyncio.to_thread(self._check_tcp, kafka_host, kafka_port)
        pg_ok = await asyncio.to_thread(self._check_tcp, pg_host, pg_port)
        neo_ok = await asyncio.to_thread(self._check_tcp, neo_host, neo_port)

        all_ready = kafka_ok and pg_ok and neo_ok
        status_code = 200 if all_ready else 503
        return web.json_response(
            {
                "status": "ready" if all_ready else "not_ready",
                "plane": self.plane_id,
                "checks": {
                    "kafka": {"reachable": kafka_ok, "host": f"{kafka_host}:{kafka_port}"},
                    "postgres": {"reachable": pg_ok, "host": f"{pg_host}:{pg_port}"},
                    "neo4j": {"reachable": neo_ok, "host": f"{neo_host}:{neo_port}"},
                },
            },
            status=status_code,
        )

    async def _metrics_handler(self, request: web.Request) -> web.Response:
        """GET /metrics — Prometheus metrics."""
        lines = [
            f"# HELP dwtads_plane_services_count Total services in plane\n"
            f"# TYPE dwtads_plane_services_count gauge\n"
            f'dwtads_plane_services_count{{plane="{self.plane_id}"}} {len(self.services)}\n',
            f"# HELP dwtads_plane_health Plane health status 1=healthy 0=unhealthy\n"
            f"# TYPE dwtads_plane_health gauge\n"
            f'dwtads_plane_health{{plane="{self.plane_id}"}} 1\n',
        ]
        for s in self.services:
            m = await s.metrics()
            lines.append(m)
        return web.Response(text="".join(lines), content_type="text/plain")

    async def start(self):
        """Instantiate services, start them as async tasks, and run plane HTTP API."""
        self.running = True
        self._setup_routes()

        # Instantiate each service class
        self.services = [cls() for cls in self.service_classes]

        # Start each service as an async task
        for service in self.services:
            t = asyncio.create_task(service.start())
            self.service_tasks.append(t)

        # Start Plane HTTP runner
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, "0.0.0.0", self.plane_port)
        await self._site.start()
        print(f"[{self.plane_name}] Plane {self.plane_id} started on port {self.plane_port} with {len(self.services)} services.")

    async def stop(self):
        """Gracefully stop plane and all services."""
        self.running = False
        print(f"[{self.plane_name}] Shutting down {len(self.services)} services...")
        for s in self.services:
            try:
                await s.stop()
            except Exception:
                pass

        for t in self.service_tasks:
            t.cancel()

        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()
        print(f"[{self.plane_name}] Shutdown complete.")

    def run(self):
        """Entrypoint for runner script."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def sig_handler():
            loop.create_task(self.stop())

        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                loop.add_signal_handler(sig, sig_handler)
            except NotImplementedError:
                pass

        try:
            loop.run_until_complete(self.start())
            loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            loop.run_until_complete(self.stop())
            loop.close()
