"""Check the dataset before every commit and before the demo.

    python validate_data.py            # structure + sources (must print OK)
    python validate_data.py --strict   # also fails while FIXTURE/example.com data remains

Exit code 1 on any problem.
"""
import sys
from datetime import date

from data.loader import load_data
from data.validate import stale_values, validate


def main(argv):
    data = load_data()
    errors, count = validate(data, strict="--strict" in argv)
    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} problem(s) found")
        return 1
    print(
        f"OK: {len(data['universities'])} universities, {len(data['programs'])} programs, "
        f"{len(data['scholarships'])} scholarships, {count} sourced values"
    )
    stale = stale_values(data, date.today().isoformat())
    if stale:
        print(f"\nWARNING: {len(stale)} value(s) were verified more than 180 days ago - re-check them:")
        print("\n".join(f"  {line}" for line in stale))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
