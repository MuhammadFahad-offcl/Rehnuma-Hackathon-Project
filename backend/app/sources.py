"""Sources page data: where every number comes from (value, link, date, official/unofficial)."""
from engine.refs import to_ref
from mentor.facts import long_date, pct, pkr

NOT_PUBLISHED = "Not officially published"

FIELDS = (
    ("weights", "Aggregate formula"),
    ("closingMerit", "Last closing merit"),
    ("minInterPercent", "Minimum inter %"),
    ("admissionFee", "Admission fee"),
    ("feePerSemester", "Fee per semester"),
    ("hostelPerYear", "Hostel per year"),
)


def _display(field, value, program):
    if field == "weights":
        return f"Matric {value['matric']:g}% + Inter {value['inter']:g}% + {program['testName']} {value['test']:g}%"
    if field == "closingMerit":
        cycle = program.get("closingMeritCycle")
        return f"{pct(value)} ({cycle})" if cycle else pct(value)
    if field == "minInterPercent":
        return f"{value:g}%"
    return pkr(value)


def _row(field, label, item, display=None):
    if item is None:
        return {"field": field, "label": label, "value": None, "display": NOT_PUBLISHED,
                "published": False, "source": None}
    return {"field": field, "label": label, "value": item["value"], "display": display or str(item["value"]),
            "published": True, "source": to_ref(item)}


def build_sources(data):
    universities = {u["id"]: u for u in data["universities"]}
    out = []
    for program in data["programs"]:
        university = universities.get(program["universityId"])
        if university is None:
            continue

        rows = []
        for field, label in FIELDS:
            item = program.get(field)
            rows.append(_row(field, label, item, _display(field, item["value"], program) if item else None))

        for deadline in program.get("deadlines", []):
            rows.append(_row(
                "deadline",
                f"{deadline['label']} ({deadline['cycle']})",
                deadline["date"],
                long_date(deadline["date"]["value"]),
            ))

        for scholarship in data["scholarships"]:
            if scholarship["universityIds"] == "all" or university["id"] in scholarship["universityIds"]:
                rows.append(_row("scholarship", f"Scholarship: {scholarship['name']}", scholarship["summary"]))

        out.append({
            "universityId": university["id"],
            "universityName": university["name"],
            "shortName": university.get("shortName"),
            "city": university["city"],
            "sector": university.get("sector"),
            "website": university.get("website"),
            "programId": program["id"],
            "programName": program["name"],
            "rows": rows,
        })
    return out
