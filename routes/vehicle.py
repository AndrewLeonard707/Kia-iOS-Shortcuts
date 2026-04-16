"""Vehicle information endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends

from auth import verify_auth

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Vehicle Info"])


@router.get("/list_vehicles")
def list_vehicles(_: str = Depends(verify_auth)) -> dict[str, Any]:
    """List all vehicles on the account."""
    from main import vm

    try:
        logger.info("Refreshing vehicle states for listing...")
        vm.update_all_vehicles_with_cached_state()

        vehicles = vm.vehicles
        if not vehicles:
            return {"error": "No vehicles found in the account"}

        vehicle_list = [
            {
                "name": v.name,
                "id": v.id,
                "model": v.model,
                "year": v.year,
            }
            for v in vehicles.values()
        ]

        logger.info("Returning %d vehicle(s)", len(vehicle_list))
        return {"status": "Success", "data": {"vehicles": vehicle_list}}
    except Exception as exc:
        logger.exception("Error listing vehicles")
        return {"error": str(exc)}


@router.get("/vehicle_status")
def vehicle_status(_: str = Depends(verify_auth)) -> dict[str, Any]:
    """Return detailed vehicle status -- doors, battery, location, odometer, etc."""
    from main import vm, VEHICLE_ID

    try:
        logger.info("Forcing full vehicle status refresh...")
        vm.check_and_refresh_token()
        vm.update_all_vehicles_with_cached_state()

        vehicle = vm.vehicles.get(VEHICLE_ID)
        if vehicle is None:
            return {"error": f"Vehicle {VEHICLE_ID} not found"}

        status: dict[str, Any] = {
            "name": vehicle.name,
            "model": vehicle.model,
            "year": vehicle.year,
            "engine_type": str(getattr(vehicle, "engine_type", None)),
            "engine_is_running": getattr(vehicle, "engine_is_running", None),
            "odometer": getattr(vehicle, "odometer", None),
            "car_battery_percentage": getattr(vehicle, "car_battery_percentage", None),
            "ev_battery_percentage": getattr(vehicle, "ev_battery_percentage", None),
            "ev_battery_is_charging": getattr(vehicle, "ev_battery_is_charging", None),
            "ev_battery_is_plugged_in": getattr(vehicle, "ev_battery_is_plugged_in", None),
            "ev_driving_range": getattr(vehicle, "ev_driving_range", None),
            "ev_estimated_current_charge_duration": getattr(vehicle, "ev_estimated_current_charge_duration", None),
            "ev_target_range_charge_AC": getattr(vehicle, "ev_target_range_charge_AC", None),
            "ev_target_range_charge_DC": getattr(vehicle, "ev_target_range_charge_DC", None),
            "fuel_level": getattr(vehicle, "fuel_level", None),
            "fuel_driving_range": getattr(vehicle, "fuel_driving_range", None),
            "total_driving_range": getattr(vehicle, "total_driving_range", None),
            "location_latitude": getattr(vehicle, "location_latitude", None),
            "location_longitude": getattr(vehicle, "location_longitude", None),
            "location_last_updated": str(getattr(vehicle, "location_last_updated_at", None)),
            "air_temperature": getattr(vehicle, "air_temperature", None),
            "defrost_is_on": getattr(vehicle, "defrost_is_on", None),
            "steering_wheel_heater_is_on": getattr(vehicle, "steering_wheel_heater_is_on", None),
            "back_window_heater_is_on": getattr(vehicle, "back_window_heater_is_on", None),
            "side_mirror_heater_is_on": getattr(vehicle, "side_mirror_heater_is_on", None),
            "front_left_seat_status": getattr(vehicle, "front_left_seat_status", None),
            "front_right_seat_status": getattr(vehicle, "front_right_seat_status", None),
            "rear_left_seat_status": getattr(vehicle, "rear_left_seat_status", None),
            "rear_right_seat_status": getattr(vehicle, "rear_right_seat_status", None),
            "is_locked": getattr(vehicle, "is_locked", None),
            "door_front_left_is_open": getattr(vehicle, "front_left_door_is_open", None),
            "door_front_right_is_open": getattr(vehicle, "front_right_door_is_open", None),
            "door_rear_left_is_open": getattr(vehicle, "back_left_door_is_open", None),
            "door_rear_right_is_open": getattr(vehicle, "back_right_door_is_open", None),
            "trunk_is_open": getattr(vehicle, "trunk_is_open", None),
            "hood_is_open": getattr(vehicle, "hood_is_open", None),
            "tire_pressure_front_left": getattr(vehicle, "tire_pressure_front_left", None),
            "tire_pressure_front_right": getattr(vehicle, "tire_pressure_front_right", None),
            "tire_pressure_rear_left": getattr(vehicle, "tire_pressure_rear_left", None),
            "tire_pressure_rear_right": getattr(vehicle, "tire_pressure_rear_right", None),
            "last_updated": str(getattr(vehicle, "last_updated_at", None)),
        }

        logger.info("Vehicle status retrieved for %s", vehicle.name)
        return {"status": "Success", "data": status}
    except Exception as exc:
        logger.exception("Error fetching vehicle status")
        return {"error": str(exc)}
