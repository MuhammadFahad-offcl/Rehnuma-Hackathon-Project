"""Dataset validator. Used by ``validate_data.py``, the test-suite and CI.

Rules (from the data spec):
- every number a student can see is a *sourced value*:
  {"value", "sourceName", "sourceUrl", "verifiedOn" (YYYY-MM-DD), "confidence": official|unofficial}
- unknown is ``null`` - never 0 and never a guess
- weights add up to 100
"""
import re

from .loader import placeholder_markers

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GROUPS = {"pre-engineering", "ics", "pre-medical", "icom", "fa"}
SECTORS = {"public", "private"}
CONFIDENCE = {"official", "unofficial"}
SCHOLARSHIP_TYPES = {"merit", "need", "merit-and-need"}


def validate(data, strict=False):
    """Return (errors, sourced_value_count). ``strict`` also rejects placeholder data."""
    errors = []
    count = 0

    def sourced(item, path, nullable=False):
        nonlocal count
        if item is None:
            if not nullable:
                errors.append(f"{path}: cannot be null")
            return None
        if not isinstance(item, dict) or "value" not in item:
            errors.append(f"{path}: must be a sourced value object with a 'value'")
            return None
        for key in ("sourceName", "sourceUrl", "verifiedOn", "confidence"):
            if not item.get(key):
                errors.append(f"{path}.{key}: missing")
        url = item.get("sourceUrl")
        if url and not str(url).startswith(("http://", "https://")):
            errors.append(f"{path}.sourceUrl: must start with http(s)://")
        verified = item.get("verifiedOn")
        if verified and not ISO_DATE.match(str(verified)):
            errors.append(f"{path}.verifiedOn: must be YYYY-MM-DD")
        if item.get("confidence") and item["confidence"] not in CONFIDENCE:
            errors.append(f"{path}.confidence: must be official or unofficial")
        count += 1
        return item["value"]

    university_ids = set()
    for i, u in enumerate(data["universities"]):
        path = f"universities[{i}]"
        for key in ("id", "name", "shortName", "city", "website"):
            if not u.get(key):
                errors.append(f"{path}.{key}: missing")
        if u.get("sector") not in SECTORS:
            errors.append(f"{path}.sector: must be public or private")
        if u.get("id") in university_ids:
            errors.append(f"{path}.id: duplicate id {u.get('id')}")
        university_ids.add(u.get("id"))

    program_ids = set()
    for i, p in enumerate(data["programs"]):
        path = f"programs[{i}]"
        for key in ("id", "universityId", "name", "testName"):
            if not p.get(key):
                errors.append(f"{path}.{key}: missing")
        if p.get("universityId") not in university_ids:
            errors.append(f"{path}.universityId: unknown university {p.get('universityId')}")
        if p.get("id") in program_ids:
            errors.append(f"{path}.id: duplicate id {p.get('id')}")
        program_ids.add(p.get("id"))

        groups = p.get("eligibleGroups") or []
        if not groups or not set(groups) <= GROUPS:
            errors.append(f"{path}.eligibleGroups: must be a non-empty subset of {sorted(GROUPS)}")

        semesters = p.get("semesters")
        if not isinstance(semesters, int) or not 2 <= semesters <= 12:
            errors.append(f"{path}.semesters: must be a whole number from 2 to 12")

        minimum = sourced(p.get("minInterPercent"), f"{path}.minInterPercent", nullable=True)
        if minimum is not None and not 0 <= minimum <= 100:
            errors.append(f"{path}.minInterPercent: out of range 0-100")

        weights = sourced(p.get("weights"), f"{path}.weights", nullable=True)
        if weights is not None:
            if not isinstance(weights, dict) or set(weights) != {"matric", "inter", "test"}:
                errors.append(f"{path}.weights: needs exactly matric, inter and test")
            elif abs(weights["matric"] + weights["inter"] + weights["test"] - 100) > 0.001:
                errors.append(f"{path}.weights: must add up to 100")

        closing = sourced(p.get("closingMerit"), f"{path}.closingMerit", nullable=True)
        if closing is not None:
            if not 0 <= closing <= 100:
                errors.append(f"{path}.closingMerit: out of range 0-100")
            if not p.get("closingMeritCycle"):
                errors.append(f"{path}.closingMeritCycle: missing (which admission cycle is this merit from?)")

        admission = sourced(p.get("admissionFee"), f"{path}.admissionFee")
        if admission is not None and admission < 0:
            errors.append(f"{path}.admissionFee: cannot be negative")

        fee = sourced(p.get("feePerSemester"), f"{path}.feePerSemester")
        if fee is not None and fee <= 0:
            errors.append(f"{path}.feePerSemester: must be positive")

        hostel = sourced(p.get("hostelPerYear"), f"{path}.hostelPerYear", nullable=True)
        if hostel is not None and hostel <= 0:
            errors.append(f"{path}.hostelPerYear: use null when unknown, never 0")

        for j, deadline in enumerate(p.get("deadlines") or []):
            dpath = f"{path}.deadlines[{j}]"
            for key in ("label", "cycle"):
                if not deadline.get(key):
                    errors.append(f"{dpath}.{key}: missing")
            when = sourced(deadline.get("date"), f"{dpath}.date")
            if when is not None and not ISO_DATE.match(str(when)):
                errors.append(f"{dpath}.date.value: must be YYYY-MM-DD")

    scholarship_ids = set()
    for i, s in enumerate(data["scholarships"]):
        path = f"scholarships[{i}]"
        for key in ("id", "name", "provider", "applyUrl"):
            if not s.get(key):
                errors.append(f"{path}.{key}: missing")
        if s.get("type") not in SCHOLARSHIP_TYPES:
            errors.append(f"{path}.type: must be merit, need or merit-and-need")
        if s.get("id") in scholarship_ids:
            errors.append(f"{path}.id: duplicate id {s.get('id')}")
        scholarship_ids.add(s.get("id"))
        sourced(s.get("summary"), f"{path}.summary")
        targets = s.get("universityIds")
        if targets != "all":
            if not isinstance(targets, list) or not targets:
                errors.append(f"{path}.universityIds: must be \"all\" or a list of university ids")
            else:
                for uid in targets:
                    if uid not in university_ids:
                        errors.append(f"{path}.universityIds: unknown university {uid}")

    if strict:
        for marker in placeholder_markers(data):
            errors.append(f"strict: placeholder '{marker}' is still present in the data")

    return errors, count


def stale_values(data, today, max_age_days=180):
    """Sourced values whose verifiedOn is older than max_age_days (to re-verify each admission cycle)."""
    from datetime import date

    now = date.fromisoformat(today)
    stale = []

    def check(item, path):
        if isinstance(item, dict) and ISO_DATE.match(str(item.get("verifiedOn", ""))):
            if (now - date.fromisoformat(item["verifiedOn"])).days > max_age_days:
                stale.append(f"{path}: verified {item['verifiedOn']}")

    for p in data["programs"]:
        for field in ("minInterPercent", "weights", "closingMerit", "admissionFee", "feePerSemester", "hostelPerYear"):
            check(p.get(field), f"{p.get('id')}.{field}")
        for d in p.get("deadlines") or []:
            check(d.get("date"), f"{p.get('id')}.deadline '{d.get('label')}'")
    for s in data["scholarships"]:
        check(s.get("summary"), f"{s.get('id')}.summary")
    return stale
