"""Climate control endpoints.

Temperature rules (preserved from the original implementation):
- Valid integer range: 62-82 degF.
- Temps below 62 are clamped to "LOW"; above 82 to "HIGH".
- Strings "LOW" and "HIGH" are accepted directly.
- Heating accessories (defrost, heated steering wheel) are enabled when
  temp >= 76 degF or temp == "HIGH".
- steering_wheel is explicitly disabled when temp < 76 degF.
"""

import logging
from typing import Any, Union

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from hyundai_kia_connect_api import ClimateRequestOptions

from auth import verify_auth

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Climate Control"])


class ClimateBody(BaseModel):
    """Request body for /start_climate."""
    temp: Union[int, str] = Field(
        ...,
        description="Desired temperature in degF (62-82) or 'LOW'/'HIGH'",
    )


@router.post("/start_climate")
def start_climate(
    body: ClimateBody,
    _: str = Depends(verify_auth),
) -> dict[str, Any]:
    """Start climate control with a custom temperature."""
    from main import vm, VEHICLE_ID

    try:
        requested_temp: Union[int, str] = body.temp
        logger.info("Requested climate temp: %s", requested_temp)

        # --- Validate / clamp ---
        if isinstance(requested_temp, str):
            if requested_temp.upper() not in ("LOW", "HIGH"):
                return {"error": f"Invalid temp string '{requested_temp}'. Use 'LOW', 'HIGH', or an integer 62-82."}
            requested_temp = requested_temp.upper()
        elif isinstance(requested_temp, int):
            if requested_temp < 62:
                requested_temp = "LOW"
            elif requested_temp > 82:
                requested_temp = "HIGH"
        else:
            return {"error": "temp must be an integer or 'LOW'/'HIGH'"}

        logger.info("Refreshing vehicle states...")
        vm.update_all_vehicles_with_cached_state()

        # Heating accessories for warm / HIGH temps
        enable_heating: bool = (
            requested_temp == "HIGH"
            or (isinstance(requested_temp, int) and requested_temp >= 76)
        )

        climate_options = ClimateRequestOptions(
            set_temp=requested_temp,
            duration=60,
            defrost=enable_heating,
            heating=1 if enable_heating else 0,
            steering_wheel=1 if enable_heating else 0,
        )

        # Explicitly disable steering wheel for temps below 76
        if isinstance(requested_temp, int) and requested_temp < 76:
            climate_options.steering_wheel = 0

        result = vm.start_climate(VEHICLE_ID, climate_options)
        logger.info("Climate start result: %s", result)
        return {
            "status": "Climate started",
            "data": {
                "temp": requested_temp,
                "heating_accessories": enable_heating,
                "result": str(result),
            },
        }
    except Exception as exc:
        logger.exception("Error starting climate")
        return {"error": str(exc)}


@router.post("/stop_climate")
def stop_climate(_: str = Depends(verify_auth)) -> dict[str, Any]:
    """Stop climate control."""
    from main import vm, VEHICLE_ID

    try:
        logger.info("Refreshing vehicle states...")
        vm.update_all_vehicles_with_cached_state()
        result = vm.stop_climate(VEHICLE_ID)
        logger.info("Climate stop result: %s", result)
        return {"status": "Climate stopped", "data": {"result": str(result)}}
    except Exception as exc:
        logger.exception("Error stopping climate")
        return {"error": str(exc)}
