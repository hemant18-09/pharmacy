"""
Reports Service – aggregation queries for pharmacy dashboard charts.

All helpers return plain dicts ready for JSON serialisation.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List

from app.core.firebase import firebase_service
from pharmacy.models import PrescriptionStatus

ORDERS_COLLECTION = "pharmacy_orders"

# Status-to-colour mapping for the donut chart
_STATUS_COLORS = {
    PrescriptionStatus.NEW: "#F59E0B",       # Amber
    PrescriptionStatus.ACCEPTED: "#3B82F6",   # Blue
    PrescriptionStatus.PREPARING: "#8B5CF6",  # Purple
    PrescriptionStatus.READY: "#0F766E",      # Teal
    PrescriptionStatus.DELIVERED: "#10B981",   # Green
    PrescriptionStatus.PICKED_UP: "#6B7280",  # Gray
    PrescriptionStatus.REJECTED: "#EF4444",   # Red
}


def _now() -> datetime:
    return datetime.utcnow()


def _date_label(dt: datetime) -> str:
    """'Feb 08' style label for chart x-axis."""
    return dt.strftime("%b %d")


def _parse_iso(ts_str: str | None) -> datetime | None:
    """Parse an ISO-8601 timestamp string to a datetime object."""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)
        return dt
    except Exception:
        return None


# ──────────────────────────────────────────────
# 0.  Analytics Stats  (key metrics + status distribution)
# ──────────────────────────────────────────────

async def get_analytics_stats() -> dict:
    """
    Returns key metrics for the Reports / Analytics page:
    - total_revenue, total_orders, avg_delivery_time_mins, status_distribution
    """
    if firebase_service.mock_mode:
        return _mock_analytics_stats()

    # --- Live / Firebase path ---
    db = firebase_service.db
    counter: Counter = Counter()
    total_revenue = 0.0
    delivery_times = []
    total_orders = 0

    docs = db.collection(ORDERS_COLLECTION).stream()
    for doc in docs:
        data = doc.to_dict()
        status = data.get("status", "")
        if status == PrescriptionStatus.REJECTED:
            counter[status] += 1
            continue

        total_orders += 1
        counter[status] += 1

        if status in (PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP):
            total_revenue += data.get("total_amount", 0.0)
            ts = data.get("timestamps", {})
            created = _parse_iso(str(ts.get("created_at", "")))
            completed = _parse_iso(str(ts.get("completed_at", "")))
            if created and completed:
                diff_mins = (completed - created).total_seconds() / 60
                if diff_mins > 0:
                    delivery_times.append(diff_mins)

    avg_time = int(sum(delivery_times) / len(delivery_times)) if delivery_times else 0

    distribution = []
    for status_val in PrescriptionStatus:
        count = counter.get(status_val, 0)
        if count > 0:
            distribution.append({
                "name": status_val.value.replace("_", " ").title(),
                "value": count,
                "color": _STATUS_COLORS.get(status_val, "#6B7280"),
            })

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "avg_delivery_time_mins": avg_time,
        "status_distribution": distribution,
    }


def _mock_analytics_stats() -> dict:
    from pharmacy.service import _MOCK_ORDERS_DB

    counter: Counter = Counter()
    total_revenue = 0.0
    delivery_times = []
    total_orders = 0

    for order in _MOCK_ORDERS_DB:
        status = order.get("status")
        if status == PrescriptionStatus.REJECTED:
            counter[status] += 1
            continue

        total_orders += 1
        counter[status] += 1

        if status in (PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP):
            total_revenue += order.get("total_amount", 0.0)
            ts = order.get("timestamps", {})
            created = _parse_iso(ts.get("created_at"))
            completed = _parse_iso(ts.get("completed_at"))
            if created and completed:
                diff_mins = (completed - created).total_seconds() / 60
                if diff_mins > 0:
                    delivery_times.append(diff_mins)

    avg_time = int(sum(delivery_times) / len(delivery_times)) if delivery_times else 0

    distribution = []
    for status_val in PrescriptionStatus:
        count = counter.get(status_val, 0)
        if count > 0:
            distribution.append({
                "name": status_val.value.replace("_", " ").title(),
                "value": count,
                "color": _STATUS_COLORS.get(status_val, "#6B7280"),
            })

    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "avg_delivery_time_mins": avg_time,
        "status_distribution": distribution,
    }


# ──────────────────────────────────────────────
# 1.  Daily Summary  (orders-per-day, last 7 days)
# ──────────────────────────────────────────────

async def daily_summary(days: int = 7) -> List[dict]:
    """
    Returns a list of { date, total_orders, delivered, new } dicts
    for the last *days* days, suitable for a bar / line chart.
    """
    if firebase_service.mock_mode:
        return _mock_daily_summary(days)

    db = firebase_service.db
    now = _now()
    start = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)

    docs = (
        db.collection(ORDERS_COLLECTION)
        .where("timestamps.created_at", ">=", start)
        .stream()
    )

    # bucket by date
    buckets: Dict[str, Dict[str, int]] = {}
    for i in range(days):
        d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        buckets[d] = {"total_orders": 0, "delivered": 0, "new": 0}

    for doc in docs:
        data = doc.to_dict()
        ts = data.get("timestamps", {}).get("created_at")
        if not ts:
            continue
        if not isinstance(ts, datetime):
            try:
                ts = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            except Exception:
                continue
        key = ts.strftime("%Y-%m-%d")
        if key in buckets:
            buckets[key]["total_orders"] += 1
            status = data.get("status", "")
            if status in (PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP):
                buckets[key]["delivered"] += 1
            if status == PrescriptionStatus.NEW:
                buckets[key]["new"] += 1

    return [
        {"date": k, "label": _date_label(datetime.strptime(k, "%Y-%m-%d")), **v}
        for k, v in buckets.items()
    ]


def _mock_daily_summary(days: int = 7) -> List[dict]:
    """Build daily summary from the actual mock orders DB."""
    from pharmacy.service import _MOCK_ORDERS_DB

    now = _now()

    # Prepare empty buckets for the last N days
    buckets: Dict[str, Dict[str, int]] = {}
    for i in range(days):
        d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        buckets[d] = {"total_orders": 0, "delivered": 0, "new": 0}

    # Fill from mock DB
    for order in _MOCK_ORDERS_DB:
        ts_str = order.get("timestamps", {}).get("created_at")
        created = _parse_iso(ts_str)
        if not created:
            continue
        key = created.strftime("%Y-%m-%d")
        if key in buckets:
            buckets[key]["total_orders"] += 1
            status = order.get("status")
            if status in (PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP):
                buckets[key]["delivered"] += 1
            if status == PrescriptionStatus.NEW:
                buckets[key]["new"] += 1

    return [
        {"date": k, "label": _date_label(datetime.strptime(k, "%Y-%m-%d")), **v}
        for k, v in buckets.items()
    ]


# ──────────────────────────────────────────────
# 2.  Top Medicines  (most dispensed drug names)
# ──────────────────────────────────────────────

async def top_medicines(limit: int = 10) -> List[dict]:
    """
    Aggregate the most frequently prescribed drug names across
    all DELIVERED / PICKED_UP orders.  Returns sorted desc by count.
    """
    if firebase_service.mock_mode:
        return _mock_top_medicines(limit)

    db = firebase_service.db
    counter: Counter = Counter()

    for s in [PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP]:
        docs = db.collection(ORDERS_COLLECTION).where("status", "==", s).stream()
        for doc in docs:
            meds = doc.to_dict().get("medications", [])
            for m in meds:
                name = m.get("drug_name", "Unknown")
                counter[name] += 1

    ranked = counter.most_common(limit)
    return [{"drug_name": name, "count": count, "rank": i + 1} for i, (name, count) in enumerate(ranked)]


def _mock_top_medicines(limit: int = 10) -> List[dict]:
    """Build top medicines from the actual mock orders DB."""
    from pharmacy.service import _MOCK_ORDERS_DB

    counter: Counter = Counter()

    for order in _MOCK_ORDERS_DB:
        status = order.get("status")
        if status in (PrescriptionStatus.DELIVERED, PrescriptionStatus.PICKED_UP):
            for med in order.get("medications", []):
                name = med.get("drug_name", "Unknown")
                counter[name] += 1

    ranked = counter.most_common(limit)
    return [
        {"drug_name": name, "count": count, "rank": i + 1}
        for i, (name, count) in enumerate(ranked)
    ]
