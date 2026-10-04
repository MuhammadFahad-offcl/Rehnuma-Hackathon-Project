import copy

from data.loader import ROOT, is_fixture, load_data
from data.validate import stale_values, validate


def test_shipped_dataset_is_structurally_valid():
    """Whatever is in data/ right now (demo or real) must pass the validator."""
    errors, count = validate(load_data(ROOT))
    assert errors == [] and count > 0


def test_test_fixtures_are_valid(data):
    errors, _ = validate(data)
    assert errors == []


def test_strict_mode_rejects_placeholder_data(data):
    assert is_fixture(data)
    errors, _ = validate(data, strict=True)
    assert any("placeholder" in e for e in errors)


def test_validator_catches_common_mistakes(data):
    bad = copy.deepcopy(data)
    program = bad["programs"][0]
    program["weights"]["value"]["test"] = 60                 # no longer adds up to 100
    program["hostelPerYear"]["value"] = 0                    # unknown must be null, never 0
    del program["feePerSemester"]["sourceUrl"]               # every number needs a source
    program["admissionFee"]["verifiedOn"] = "3 Oct 2026"     # wrong date format
    program["closingMerit"]["confidence"] = "maybe"
    bad["programs"][1]["universityId"] = "nope"
    bad["scholarships"][0]["universityIds"] = ["nope"]
    bad["scholarships"][0]["type"] = "lottery"
    bad["programs"][2]["semesters"] = 1
    errors, _ = validate(bad)
    text = "\n".join(errors)
    for expected in ("add up to 100", "never 0", "sourceUrl: missing", "YYYY-MM-DD",
                     "official or unofficial", "unknown university nope",
                     "merit, need or merit-and-need", "from 2 to 12"):
        assert expected in text, expected


def test_required_fee_cannot_be_null(data):
    bad = copy.deepcopy(data)
    bad["programs"][0]["feePerSemester"] = None
    errors, _ = validate(bad)
    assert any("feePerSemester: cannot be null" in e for e in errors)


def test_old_values_are_flagged_for_re_verification(data):
    assert stale_values(data, today="2026-10-04") == []
    stale = stale_values(data, today="2027-06-01")
    assert stale and all("verified 2026-10-03" in line for line in stale)
