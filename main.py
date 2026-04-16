"""Kia Vehicle Control API -- FastAPI application.

Provides remote control of Kia/Hyundai vehicles via the hyundai_kia_connect_api
library, designed for deployment on Vercel and use with iOS Shortcuts.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI

from hyundai_kia_connect_api import VehicleManager
from hyundai_kia_connect_api.exceptions import AuthenticationError

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level state (populated during lifespan startup)
# ---------------------------------------------------------------------------
vm: Optional[VehicleManager] = None
VEHICLE_ID: Optional[str] = None
_startup_ok: bool = False


def _init_vehicle_manager() -> None:
    """Create and authenticate the VehicleManager, select the active vehicle."""
    global vm, VEHICLE_ID, _startup_ok  # noqa: PLW0603

    username = os.environ.get("KIA_USERNAME")
    password = os.environ.get("KIA_PASSWORD")
    pin = os.environ.get("KIA_PIN")

    if not all([username, password, pin]):
        logger.error(
            "Missing credentials -- set KIA_USERNAME, KIA_PASSWORD, and KIA_PIN"
        )
        return

    vm = VehicleManager(
        region=3,   # North America
        brand=1,    # KIA
        username=username,
        password=password,
        pin=str(pin),
    )

    try:
        logger.info("Authenticating with Kia Connect...")
        vm.check_and_refresh_token()
        logger.info("Token refreshed successfully")
        vm.update_all_vehicles_with_cached_state()
        logger.info("Connected -- found %d vehicle(s)", len(vm.vehicles))
    except AuthenticationError as exc:
        logger.error("Authentication failed: %s", exc)
        return
    except Exception as exc:
        logger.error("Unexpected error during init: %s", exc)
        return

    # Select vehicle
    VEHICLE_ID = os.environ.get("VEHICLE_ID")
    if not VEHICLE_ID:
        if not vm.vehicles:
            logger.error("No vehicles found in the account")
            return
        VEHICLE_ID = next(iter(vm.vehicles.keys()))
        logger.info("No VEHICLE_ID set -- using first vehicle: %s", VEHICLE_ID)

    _startup_ok = True


# ---------------------------------------------------------------------------
# FastAPI lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Run startup logic (init VehicleManager), then yield to the app."""
    _init_vehicle_manager()
    yield


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Kia Vehicle Control API",
    description=(
        "Remote-control your Kia/Hyundai vehicle -- lock, unlock, climate, "
        "charge, and status. Built for iOS Shortcuts & Vercel deployment."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Register route modules
# ---------------------------------------------------------------------------
from routes.lock import router as lock_router       # noqa: E402
from routes.climate import router as climate_router  # noqa: E402
from routes.vehicle import router as vehicle_router  # noqa: E402
from routes.charge import router as charge_router    # noqa: E402

app.include_router(lock_router)
app.include_router(climate_router)
app.include_router(vehicle_router)
app.include_router(charge_router)


# ---------------------------------------------------------------------------
# Health check (no auth required)
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check() -> dict[str, Any]:
    """Health check -- always responds, even if vehicle auth failed."""
    return {
        "status": "ok" if _startup_ok else "degraded",
        "message": (
            "Kia Vehicle Control API is running"
            if _startup_ok
            else "API is running but vehicle connection failed -- check credentials"
        ),
    }
