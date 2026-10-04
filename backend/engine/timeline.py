from .refs import to_ref


def next_deadline(program, today):
    dates = [
        d for d in program.get("deadlines", [])
        if d["date"]["value"] >= today
    ]
    dates.sort(key=lambda d: d["date"]["value"])

    if not dates:
        return None

    d = dates[0]
    return {
        "label": d["label"],
        "date": d["date"]["value"],
        "cycle": d["cycle"],
    }


def build_timeline(options, data, today):
    """All deadlines of the eligible options, oldest first."""
    programs = {p["id"]: p for p in data["programs"]}
    items = []

    for option in options:
        if not option["eligible"]:
            continue

        program = programs.get(option["programId"])
        if not program:
            continue

        for d in program.get("deadlines", []):
            items.append({
                "date": d["date"]["value"],
                "label": d["label"],
                "universityName": option["universityName"],
                "programId": option["programId"],
                "cycle": d["cycle"],
                "isPast": d["date"]["value"] < today,
                "source": to_ref(d["date"]),
            })

    return sorted(items, key=lambda x: (x["date"], x["universityName"]))
