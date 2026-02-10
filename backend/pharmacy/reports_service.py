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


def _now() -> datetime:
    return datetime.utcnow()


def _date_label(dt: datetime) -> str:
    """'Feb 08' style label for chart x-axis."""
    return dt.strftime("%b %d")


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
    now = _now()
    # Realistic-looking mock numbers
    mock_totals = [12, 18, 9, 22, 15, 20, 14]
    mock_delivered = [8, 14, 6, 18, 10, 16, 9]
    mock_new = [4, 4, 3, 4, 5, 4, 5]
    result = []
    for i in range(days):
        d = now - timedelta(days=days - 1 - i)
        result.append({
            "date": d.strftime("%Y-%m-%d"),
            "label": _date_label(d),
            "total_orders": mock_totals[i % len(mock_totals)],
            "delivered": mock_delivered[i % len(mock_delivered)],
            "new": mock_new[i % len(mock_new)],
        })
    return result


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
    seed = [
        ("Paracetamol", 142),
        ("Amoxicillin", 98),
        ("Azithromycin", 76),
        ("Pantoprazole", 65),
        ("Cetirizine", 58),
        ("Metformin", 52),
        ("Ibuprofen", 47),
        ("Omeprazole", 39),
        ("Dolo-650", 34),
        ("Montelukast", 28),
    ]
    return [
        {"drug_name": name, "count": count, "rank": i + 1}
        for i, (name, count) in enumerate(seed[:limit])
    ]
