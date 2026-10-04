from engine.timeline import build_timeline, next_deadline

class TimelineAgent:
    name = "Timeline Agent"

    def next(self, program, today):
        return next_deadline(program, today)

    def run(self, options, data, today):
        return build_timeline(options, data, today)
