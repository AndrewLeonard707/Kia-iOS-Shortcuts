"""Lock / Unlock endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends

from auth import verify_auth

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Lock / Unlock"])


@router.post("/lock_car")
def lock_car(_: str = Depends(verify_auth)) -> dict[str, Any]:
    """Lock the vehicle."""
    from main import vm, VEHICLE_ID  # deferred to avoid circular import

    try:
        logger.info("Refreshing vehicle states before locking...")
        vm.update_all_vehicles_with_cached_state()
        result = vm.lock(VEHICLE_ID)
        logger.info("Lock result: %s", result)
        return {"status": "Car locked", "data": {"result": str(result)}}
    except Exception as exc:
        logger.exception("Error locking car")
        return {"error": str(exc)}


@router.post("/unlock_car")
def unlock_car(_: str = Depends(verify_auth)) -> dict[str, Any]:
    """Unlock the vehicle."""
    from main import vm, VEHICLE_ID

    try:
        logger.info("Refreshing vehicle states before unlocking...")
        vm.update_all_vehicles_with_cached_state()
        result = vm.unlock(VEHICLE_ID)
        logger.info("Unlock result: %s", result)
        return {"status": "Car unlocked", "data": {"result": str(result)}}
    except Exception as exc:
        logger.exception("Error unlocking car")
        return {"error": str(exc)}
