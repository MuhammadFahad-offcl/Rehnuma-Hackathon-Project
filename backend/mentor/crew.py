"""Optional CrewAI mode: two LLM agents, Explainer -> Fact-Checker.

Enable with MENTOR_ENGINE=crewai and `pip install -r requirements-crew.txt`.
The crew's final text still goes through the same digit guard, retry and
fallback as the default single-call mode, so the safety rule is unchanged:
numbers only ever come from fact IDs.

CrewAI is a heavy dependency (slow builds, more memory), so it is off by
default and not installed on the free deploy.
"""
from .client import providers, timeout_seconds


def call_crew(system: str, prompt: str) -> str:
    from crewai import LLM, Agent, Crew, Process, Task  # lazy: the API works without crewai

    configured = providers()
    if not configured:
        raise RuntimeError("no LLM provider configured")
    provider = configured[0]

    llm = LLM(
        model=f"openai/{provider.model}",  # OpenAI-compatible endpoint
        base_url=provider.base_url,
        api_key=provider.api_key,
        temperature=0.2,
        timeout=timeout_seconds(),
    )

    explainer = Agent(
        role="University Admission Mentor",
        goal="Explain a finished university plan simply to a Pakistani student.",
        backstory=system,
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )
    checker = Agent(
        role="Fact Checker",
        goal="Make sure the answer contains no digits and only fact IDs from the FACTS list.",
        backstory=system,
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )

    draft = Task(description=prompt, expected_output="A short, clear answer.", agent=explainer)
    review = Task(
        description=(
            "Review the previous answer against the RULES and the FACTS list. Replace any typed digit or "
            "amount written in words with the matching fact ID in double square brackets, or remove it. "
            "Return the corrected final answer only."
        ),
        expected_output="The corrected final answer only.",
        agent=checker,
        context=[draft],
    )

    crew = Crew(agents=[explainer, checker], tasks=[draft, review], process=Process.sequential, verbose=False)
    return str(crew.kickoff()).strip()
