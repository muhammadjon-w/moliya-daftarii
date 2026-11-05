"""Tariflar: kalit = oylar soni, qiymat = so'm."""
import json

DEFAULT_PRICES = {"1": 29000, "6": 149000, "12": 249000}


def parse_prices(raw: str | None) -> dict[str, int]:
    try:
        data = json.loads(raw) if raw else None
        if isinstance(data, dict) and data:
            clean = {str(int(k)): int(v) for k, v in data.items() if int(k) > 0 and int(v) > 0}
            if clean:
                return clean
    except (ValueError, TypeError):
        pass
    return dict(DEFAULT_PRICES)


def price_for(prices: dict[str, int], months: int) -> int | None:
    return prices.get(str(months))
