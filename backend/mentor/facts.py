"""buildFacts(plan): turn the finished plan into a numbered fact list (F1, F2, ...)."""
from datetime import date

MAX_OPTIONS = 5  # only the top five eligible options, to keep the prompt short and fast


def pkr(amount) -> str:
    return "PKR " + f"{round(amount):,}"


def pct(number) -> str:
    return f"{number:.1f}%"


def long_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


def top_options(plan):
    return [o for o in plan["options"] if o["eligible"]][:MAX_OPTIONS]


def build_facts(plan):
    """Return (facts, ids) where ids maps e.g. 'demo-lhr-bscs.total' -> 'F9'."""
    facts = []
    ids = {}

    # Labels must not contain digits. Years and cycles go in `display`.
    def add(key, label, display, source=None):
        fact_id = f"F{len(facts) + 1}"
        facts.append({
            "id": fact_id,
            "label": label,
            "display": display,
            "kind": "sourced" if source else "calculated",
            "source": source or None,
        })
        ids[key] = fact_id

    p = plan["profile"]
    add("budget", "Student budget for the whole degree", pkr(p["budgetTotal"]))
    add("matric", "Student matric percentage", pct(p["matricObtained"] / p["matricTotal"] * 100))
    add("inter", "Student inter percentage", pct(p["interObtained"] / p["interTotal"] * 100))

    for o in top_options(plan):
        u = o["universityName"]
        k = o["programId"]
        sources = o.get("sources") or {}

        if o.get("requiredTestPercent") is not None:
            add(f"{k}.required", f"{u}: score needed in {o['testName']}", pct(o["requiredTestPercent"]))
        if o.get("aggregate") is not None:
            add(f"{k}.aggregate", f"{u}: student aggregate", pct(o["aggregate"]))
        if o.get("closingMerit") is not None:
            add(
                f"{k}.merit",
                f"{u}: last closing merit",
                f"{pct(o['closingMerit'])} ({o.get('closingMeritCycle')})",
                sources.get("closingMerit"),
            )

        cost = o["cost"]
        add(f"{k}.tuition", f"{u}: tuition for the whole degree", pkr(cost["tuition"]), sources.get("feePerSemester"))
        add(f"{k}.total", f"{u}: total cost of the degree", pkr(cost["total"]))
        add(
            f"{k}.gap",
            f"{u}: amount {'over' if cost['gap'] > 0 else 'under'} budget",
            pkr(abs(cost["gap"])),
        )

        deadline = o.get("nextDeadline")
        if deadline:
            item = next(
                (t for t in plan["timeline"] if t["programId"] == k and t["date"] == deadline["date"]),
                None,
            )
            add(
                f"{k}.deadline",
                f"{u}: {deadline['label']}",
                long_date(deadline["date"]),
                item["source"] if item else None,
            )

    return facts, ids
