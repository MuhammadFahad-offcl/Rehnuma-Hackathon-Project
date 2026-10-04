"""Helpers for sourced values: {"value": ..., "sourceName", "sourceUrl", "verifiedOn", "confidence"}."""


def to_ref(sourced):
    """Return the citation part of a sourced value (everything except the value)."""
    ref = {
        "sourceName": sourced["sourceName"],
        "sourceUrl": sourced["sourceUrl"],
        "verifiedOn": sourced["verifiedOn"],
        "confidence": sourced["confidence"],
    }
    if sourced.get("note"):
        ref["note"] = sourced["note"]
    return ref


def value_of(sourced):
    return None if sourced is None else sourced["value"]


def same_city(a: str, b: str) -> bool:
    return a.strip().lower() == b.strip().lower()
