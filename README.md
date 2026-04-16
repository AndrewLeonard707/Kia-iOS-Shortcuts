# Kia iOS Shortcuts API

A FastAPI service that lets you control your Kia (or Hyundai) vehicle remotely through simple HTTP endpoints. Designed for **iOS Shortcuts** but works with any HTTP client.

Built on top of [hyundai_kia_connect_api](https://github.com/Hyundai-Kia-Connect/hyundai_kia_connect_api).

---

## Features

- **Lock / Unlock** -- lock or unlock your vehicle remotely
- **Climate Control** -- start climate with a custom temperature (62-82 degF, or LOW/HIGH), stop climate
- **Vehicle Status** -- doors, battery, fuel, location, odometer, tire pressure, and more
- **Charge Control** -- start or stop EV/PHEV charging

All endpoints are protected by a secret key passed in the `Authorization` header.

---

## Setup

### 1. Fork or clone the repo

```bash
git clone https://github.com/YOUR_USER/Kia-iOS-Shortcuts.git
```

### 2. Set environment variables

| Variable       | Required | Description |
|----------------|----------|-------------|
| `KIA_USERNAME` | Yes      | Your Kia Connect account email |
| `KIA_PASSWORD` | Yes      | Your Kia Connect account password |
| `KIA_PIN`      | Yes      | Your 4-digit Kia PIN |
| `SECRET_KEY`   | Yes      | A custom secret string you create -- used to authenticate API requests |
| `VEHICLE_ID`   | No       | Your vehicle's ID. If omitted, the API uses the first vehicle on the account |

### 3. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **New Project** and select this repository.
3. Add the environment variables above in the Vercel dashboard under **Settings > Environment Variables**.
4. Deploy. Vercel will install dependencies and serve the FastAPI app.

### 4. (Optional) Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

---

## API Reference

All endpoints (except the health check) require the `Authorization` header set to your `SECRET_KEY`.

### Health Check

```
GET /
```

No auth required. Returns API status.

**Response:**
```json
{
  "status": "ok",
  "message": "Kia Vehicle Control API is running"
}
```

---

### List Vehicles

```
GET /list_vehicles
Headers: Authorization: <SECRET_KEY>
```

**Response:**
```json
{
  "status": "Success",
  "data": {
    "vehicles": [
      {
        "name": "My Kia EV6",
        "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "model": "EV6",
        "year": 2024
      }
    ]
  }
}
```

---

### Lock Car

```
POST /lock_car
Headers: Authorization: <SECRET_KEY>
```

**Response:**
```json
{
  "status": "Car locked",
  "data": { "result": "..." }
}
```

---

### Unlock Car

```
POST /unlock_car
Headers: Authorization: <SECRET_KEY>
```

**Response:**
```json
{
  "status": "Car unlocked",
  "data": { "result": "..." }
}
```

---

### Start Climate

```
POST /start_climate
Headers: Authorization: <SECRET_KEY>
Content-Type: application/json

Body: { "temp": 72 }
```

The `temp` field accepts:
- An integer between **62 and 82** (degrees Fahrenheit)
- The string `"LOW"` or `"HIGH"`
- Integers below 62 are clamped to `"LOW"`, above 82 to `"HIGH"`

When `temp >= 76` or `"HIGH"`, defrost, heated steering wheel, and heating are enabled.

**Response:**
```json
{
  "status": "Climate started",
  "data": {
    "temp": 72,
    "heating_accessories": false,
    "result": "..."
  }
}
```

---

### Stop Climate

```
POST /stop_climate
Headers: Authorization: <SECRET_KEY>
```

**Response:**
```json
{
  "status": "Climate stopped",
  "data": { "result": "..." }
}
```

---

### Vehicle Status

```
GET /vehicle_status
Headers: Authorization: <SECRET_KEY>
```

**Response:**
```json
{
  "status": "Success",
  "data": {
    "name": "My Kia EV6",
    "model": "EV6",
    "year": 2024,
    "engine_is_running": false,
    "odometer": 12345.6,
    "ev_battery_percentage": 80,
    "ev_battery_is_charging": false,
    "fuel_level": null,
    "location_latitude": 37.7749,
    "location_longitude": -122.4194,
    "is_locked": true,
    "door_front_left_is_open": false,
    "tire_pressure_front_left": 35,
    "last_updated": "2025-01-15 10:30:00"
  }
}
```

(Additional fields are included -- see the full response for all available data.)

---

### Start Charge (EV/PHEV)

```
POST /start_charge
Headers: Authorization: <SECRET_KEY>
```

**Response:**
```json
{
  "status": "Charging started",
  "data": { "result": "..." }
}
```

---

### Stop Charge (EV/PHEV)

```
POST /stop_charge
Headers: Authorization: <SECRET_KEY>
```

**Response:**
```json
{
  "status": "Charging stopped",
  "data": { "result": "..." }
}
```

---

### Error Response Format

All endpoints return errors in this format:

```json
{
  "error": "Description of what went wrong"
}
```

A `403` status is returned for missing or incorrect `Authorization` header.

---

## OpenAPI Docs

FastAPI auto-generates interactive API documentation:

- **Swagger UI:** `https://your-app.vercel.app/docs`
- **ReDoc:** `https://your-app.vercel.app/redoc`

---

## iOS Shortcuts Setup

For each shortcut below, follow these steps in the **Shortcuts** app on your iPhone:

1. Open **Shortcuts** and tap **+** to create a new shortcut.
2. Tap **Add Action**, search for **Get Contents of URL**, and select it.
3. Configure the action as described below.
4. (Optional) Add a **Show Result** action to see the response.
5. Tap the drop-down at the top to rename and choose an icon.
6. Tap **Done**.

**Base URL:** `https://your-app.vercel.app` (replace with your Vercel deployment URL)

> For every shortcut: add a Header with **Key** = `Authorization` and **Value** = your `SECRET_KEY`.

---

### Lock Car Shortcut

- **URL:** `https://your-app.vercel.app/lock_car`
- **Method:** POST
- **Headers:** `Authorization: <your SECRET_KEY>`
- No request body needed.

### Unlock Car Shortcut

- **URL:** `https://your-app.vercel.app/unlock_car`
- **Method:** POST
- **Headers:** `Authorization: <your SECRET_KEY>`
- No request body needed.

### Start Climate Shortcut

- **URL:** `https://your-app.vercel.app/start_climate`
- **Method:** POST
- **Headers:**
  - `Authorization: <your SECRET_KEY>`
  - `Content-Type: application/json`
- **Request Body:** JSON
  - Add a field: **Key** = `temp`, **Type** = Number, **Value** = your desired temperature (e.g. `72`)

To set up the body in iOS Shortcuts:
1. In the **Get Contents of URL** action, set Method to **POST**.
2. Under **Request Body**, choose **JSON**.
3. Tap **Add New Field** > **Number**.
4. Set the key to `temp` and the value to your desired temperature (e.g., `72`).
5. You can also use an **Ask Each Time** variable for the temp value to pick it when the shortcut runs.

### Stop Climate Shortcut

- **URL:** `https://your-app.vercel.app/stop_climate`
- **Method:** POST
- **Headers:** `Authorization: <your SECRET_KEY>`
- No request body needed.

### Vehicle Status Shortcut

- **URL:** `https://your-app.vercel.app/vehicle_status`
- **Method:** GET
- **Headers:** `Authorization: <your SECRET_KEY>`
- No request body needed.
- Add a **Show Result** action to display the vehicle data.

### Start Charge Shortcut (EV/PHEV)

- **URL:** `https://your-app.vercel.app/start_charge`
- **Method:** POST
- **Headers:** `Authorization: <your SECRET_KEY>`
- No request body needed.

### Stop Charge Shortcut (EV/PHEV)

- **URL:** `https://your-app.vercel.app/stop_charge`
- **Method:** POST
- **Headers:** `Authorization: <your SECRET_KEY>`
- No request body needed.

---

## Region Codes

The API defaults to **North America (region 3)**. If you are in a different region, update the `region` value in `main.py`:

| Code | Region    |
|------|-----------|
| 1    | Europe    |
| 2    | Canada    |
| 3    | USA       |
| 4    | China     |
| 5    | Australia |

---

## Notes on EV-Only Endpoints

The `/start_charge` and `/stop_charge` endpoints only work with electric (EV) or plug-in hybrid (PHEV) vehicles. Calling these on a non-EV vehicle will return an error from the Kia Connect API.

The `/vehicle_status` endpoint includes EV-specific fields (`ev_battery_percentage`, `ev_battery_is_charging`, `ev_driving_range`, etc.) that will return `null` for non-EV vehicles.

---

## License

This project is licensed under the MIT License -- see the [LICENSE](LICENSE) file for details.
