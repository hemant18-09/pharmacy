"""
FastAPI Router – Pharmacy Reports / Analytics
Prefix: /pharmacy/reports

Endpoints:
  GET /pharmacy/reports/stats           → Key metrics + status distribution
  GET /pharmacy/reports/daily-summary   → "Orders per day" chart (last 7 days)
  GET /pharmacy/reports/top-medicines   → "Most Dispensed" chart (top N)
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Query

from pharmacy.schemas import DailySummaryItem, TopMedicineItem, AnalyticsStatsResponse
from pharmacy import reports_service as svc

router = APIRouter(prefix="/pharmacy/reports", tags=["Pharmacy Reports"])


# ──────────────────────────────────────────────
# 0. Analytics key metrics + status distribution
# ──────────────────────────────────────────────

@router.get("/stats", response_model=AnalyticsStatsResponse)
async def analytics_stats():
    """
    Returns key metrics for the Reports / Analytics page:
    total_revenue, total_orders, avg_delivery_time_mins, and status_distribution.
    """
    return await svc.get_analytics_stats()


# ──────────────────────────────────────────────
# 1. Orders per day (last N days)
# ──────────────────────────────────────────────

@router.get("/daily-summary", response_model=List[DailySummaryItem])
async def daily_summary(
    days: int = Query(7, ge=1, le=90, description="Number of trailing days"),
):
    """
    Returns per-day totals for the "Orders per day" bar chart.
    Each point includes `total_orders`, `delivered`, and `new`.
    """
    return await svc.daily_summary(days=days)


# ──────────────────────────────────────────────
# 2. Most dispensed medicines
# ──────────────────────────────────────────────

@router.get("/top-medicines", response_model=List[TopMedicineItem])
async def top_medicines(
    limit: int = Query(10, ge=1, le=50, description="Number of top drugs to return"),
):
    """
    Aggregates drug names from all completed orders and returns the
    most frequently dispensed, suitable for a horizontal bar chart.
    """
    return await svc.top_medicines(limit=limit)
