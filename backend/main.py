from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add the current directory to sys.path to ensure 'pharmacy' can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import routers
# We need to make sure 'pharmacy' is treated as a package
from pharmacy.router import router as pharmacy_v1_router
from pharmacy.inventory_router import router as inventory_router
from pharmacy_v2 import router as pharmacy_v2_router

app = FastAPI(title="Pharma Backend", version="1.0.0")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "*" # Allow all for development convenience
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(pharmacy_v1_router)
app.include_router(inventory_router)
app.include_router(pharmacy_v2_router)

@app.get("/")
async def root():
    return {"message": "Pharma Backend is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
