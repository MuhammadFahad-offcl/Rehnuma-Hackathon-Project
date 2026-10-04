from engine.cost import compute_cost

class BudgetAgent:
    name = "Budget Agent"

    def run(self, profile, program, university_city):
        return compute_cost(profile, program, university_city)
