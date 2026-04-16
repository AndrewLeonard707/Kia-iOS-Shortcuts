"""Charge control endpoints (EV / PHEV only)."""

import logging
from typing import Any

from fastapi import APIRouter, Depends

from auth import verify_auth

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Charge Control"])


@router.post("/start_charge")
def start_charge(_: str = Depends(verify_auth)) -> dict[str, Any]:
    """Start charging the vehicle (EV/PHEV only)."""
    from main import vm, VEHICLE_ID

    try:
        logger.info("Refreshing vehicle states before starting charge...")
        vm.update_all_vehicles_with_cached_state()
        result = vm.start_charge(VEHICLE_ID)
        logger.info("Start charge result: %s", result)
        return {"status": "Charging started", "data": {"result": str(result)}}
    except Exception as exc:
        logger.exception("Error starting charge")
        return {"error": str(exc)}


@router.post("/stop_charge")
def stop_charge(_: str = Depends(verify_auth)) -> dict[str, Any]:
    """Stop charging the vehicle (EV/PHEV only)."""
    from main import vm, VEHICLE_ID

    try:
        logger.info("Refreshing vehicle states before stopping charge...")
        vm.update_all_vehicles_with_cached_state()
        result = vm.stop_charge(VEHICLE_ID)
        logger.info("Stop charge result: %s", result)
        return {"status": "Charging stopped", "data": {"result": str(result)}}
    except Exception as exc:
        logger.exception("Error stopping charge")
        return {"error": str(exc)}
