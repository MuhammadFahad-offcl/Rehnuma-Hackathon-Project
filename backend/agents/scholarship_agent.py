from engine.scholarships import match_scholarships

class ScholarshipAgent:
    name = "Scholarship Agent"

    def run(self, profile, university_id, inter_pct, scholarships):
        return match_scholarships(
            profile, university_id, inter_pct, scholarships
        )
