from engine.eligibility import check_eligibility

class EligibilityAgent:
    name = "Eligibility Agent"

    def run(self, profile, program, inter_pct):
        return check_eligibility(profile, program, inter_pct)
