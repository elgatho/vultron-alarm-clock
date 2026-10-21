"""Czysta logika wyliczania budzika (bez zaleznosci od HA)."""
from __future__ import annotations

from datetime import date, datetime, timedelta


def compute_alarm(
    plans: list[dict], target: date, travel: int, prep: int, skip: set[str]
) -> tuple[datetime | None, str | None]:
    """Zwraca (naiwny czas budzika, godzina pierwszej lekcji) albo (None, powod)."""
    if target.weekday() >= 5:
        return None, "weekend"
    iso = target.isoformat()
    if any(w.get("d") == iso for p in plans for w in p.get("dni_wolne") or []):
        return None, "dzien_wolny"
    starts = [
        l["g"][:5]
        for p in plans
        for l in p.get("lekcje") or []
        if l.get("d") == iso and (l.get("st") or "").upper() not in skip
    ]
    if not starts:
        return None, "brak_lekcji"
    first = min(starts)  # "HH:MM" sortuje sie leksykograficznie
    start = datetime.combine(target, datetime.strptime(first, "%H:%M").time())
    return start - timedelta(minutes=travel + prep), first
