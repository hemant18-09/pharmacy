# Pharmacy Portal

Pharmacy management portal with a React + Vite frontend and a FastAPI backend. The app supports order intake and status flow, inventory management, and reports, with mock data fallback when Firebase is not configured.

## Features

- Dashboard with KPIs and active order queue
- Order intake and status flow (Accept, Ready, Delivered)
- Orders list (Accepted) and History (Delivered and Picked Up)
- Inventory management with add, edit stock, delete, and low stock filtering
- Mobile-friendly layouts for key screens
- Mock data for inventory and orders when Firebase is not available

## Tech Stack

- Frontend: React, Vite, Tailwind CSS, Lucide Icons, Recharts
- Backend: FastAPI, Pydantic, Firebase Admin SDK (optional)

## Project Structure

- Frontend: [src](src)
- Backend: [backend](backend)
- Inventory services: [backend/pharmacy/inventory_service.py](backend/pharmacy/inventory_service.py)
- Orders services: [backend/pharmacy/service.py](backend/pharmacy/service.py)
- API routers: [backend/pharmacy/router.py](backend/pharmacy/router.py) and [backend/pharmacy/inventory_router.py](backend/pharmacy/inventory_router.py)

## Quick Start

### 1) Frontend

```bash
npm install
npm run dev
```

Vite will start the dev server (default: `http://localhost:5173`).

### 2) Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

FastAPI will run at `http://localhost:8000`.

## Configuration

The backend can use Firebase or a mock mode fallback. The project already includes mock data for orders and inventory.

- Firebase credential sample: [backend/firebase-service-account.example.json](backend/firebase-service-account.example.json)
- App Firebase initialization: [backend/app/core/firebase.py](backend/app/core/firebase.py)

If Firebase is not set up, the backend runs in mock mode (see `firebase_service.mock_mode`).

## Mock Data

Mock data is defined in:

- Orders: [backend/pharmacy/service.py](backend/pharmacy/service.py)
- Inventory: [backend/pharmacy/inventory_service.py](backend/pharmacy/inventory_service.py)

To change the mock order list, edit the `_MOCK_ORDERS_DB` list. For inventory, edit `_mock_inventory()`.

## API Overview

Base path: `/pharmacy`

### Orders

- `GET /pharmacy/orders`
  - Optional query: `status` (NEW, ACCEPTED, READY, DELIVERED, PICKED_UP, REJECTED)
- `GET /pharmacy/orders/{order_id}`
- `PATCH /pharmacy/orders/{order_id}/status`
  - Body: `{ "status": "ACCEPTED" | "READY" | "DELIVERED" | "PICKED_UP" | "REJECTED" }`

### Inventory

- `GET /pharmacy/inventory`
- `POST /pharmacy/inventory/add`
- `POST /pharmacy/inventory/update`
- `DELETE /pharmacy/inventory/{item_id}`

## UI Behavior Notes

- Active Queue shows NEW orders.
- Orders page shows ACCEPTED orders and provides Ready/Delivered actions.
- History shows DELIVERED and PICKED_UP orders with timestamps.
- Inventory supports search, low-stock filter, add, edit, and delete.

## Scripts

Frontend:

```bash
npm run dev
npm run build
npm run preview
```

Backend:

```bash
python main.py
```

## Troubleshooting

- If the backend fails to start, verify Python dependencies from [backend/requirements.txt](backend/requirements.txt).
- If Firebase is not configured, keep mock mode enabled in [backend/app/core/firebase.py](backend/app/core/firebase.py).
- If inventory delete fails, confirm the backend server is running and accessible.


add the mock data in the database as well

## License

Add your license here.
