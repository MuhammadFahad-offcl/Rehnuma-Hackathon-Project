"""Request/response contract of the Rehnuma API.

Field names are camelCase on purpose: they are the same names the engine,
the mentor and the frontend types (frontend/src/lib/rehnuma/types.ts) use.
"""
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

Group = Literal["pre-engineering", "ics", "pre-medical", "icom", "fa"]
InterStatus = Literal["part1", "complete"]
Category = Literal["safe", "target", "reach", "unlikely", "no-data", "not-eligible"]

DEFAULT_TOTAL = 1100
DEFAULT_PART1_TOTAL = 550


class StudentProfile(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    matricObtained: float = Field(ge=0, le=5000)
    matricTotal: Optional[float] = Field(default=None, gt=0, le=5000)
    interObtained: float = Field(ge=0, le=5000)
    interTotal: Optional[float] = Field(default=None, gt=0, le=5000)
    interStatus: InterStatus = "complete"
    group: Group
    homeCity: str = Field(min_length=1, max_length=60)
    willingToRelocate: bool = True
    budgetTotal: float = Field(ge=0, le=1_000_000_000)
    familyIncomeMonthly: Optional[float] = Field(default=None, ge=0, le=1_000_000_000)
    expectedTestPercent: Optional[float] = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def _totals(self):
        # If the form only collects obtained marks, fall back to the board defaults.
        if self.matricTotal is None:
            self.matricTotal = DEFAULT_TOTAL
        if self.interTotal is None:
            self.interTotal = DEFAULT_PART1_TOTAL if self.interStatus == "part1" else DEFAULT_TOTAL
        if self.matricObtained > self.matricTotal:
            raise ValueError("matricObtained cannot be more than matricTotal")
        if self.interObtained > self.interTotal:
            raise ValueError("interObtained cannot be more than interTotal")
        return self


class SourceRef(BaseModel):
    sourceName: str
    sourceUrl: str
    verifiedOn: str
    confidence: Literal["official", "unofficial"]
    note: Optional[str] = None


class Cost(BaseModel):
    tuition: float
    admissionFee: float
    hostel: float
    total: float
    withinBudget: bool
    gap: float
    hostelApplies: bool
    hostelUnknown: bool


class ScholarshipMatch(BaseModel):
    id: str
    name: str
    provider: Optional[str] = None
    type: Optional[str] = None
    summary: str
    applyUrl: str
    source: SourceRef


class Deadline(BaseModel):
    label: str
    date: str
    cycle: str


class Weights(BaseModel):
    matric: float
    inter: float
    test: float


class PlanOption(BaseModel):
    programId: str
    universityId: str
    universityName: str
    universityShortName: Optional[str] = None
    sector: Optional[str] = None
    website: Optional[str] = None
    programName: str
    city: str
    testName: str
    eligible: bool
    ineligibleReason: Optional[str] = None
    category: Category
    categoryReason: str
    matricPercent: float
    interPercent: float
    academicPart: Optional[float] = None
    aggregate: Optional[float] = None
    requiredTestPercent: Optional[float] = None
    closingMerit: Optional[float] = None
    closingMeritCycle: Optional[str] = None
    weights: Optional[Weights] = None
    semesters: int
    cost: Cost
    scholarships: List[ScholarshipMatch]
    nextDeadline: Optional[Deadline] = None
    sources: Dict[str, SourceRef]


class TimelineItem(BaseModel):
    date: str
    label: str
    universityName: str
    programId: str
    cycle: str
    isPast: bool
    source: SourceRef


class PlanSummary(BaseModel):
    safe: int
    target: int
    reach: int
    unlikely: int
    noData: int
    notEligible: int
    withinBudget: int


class PlanResult(BaseModel):
    profile: StudentProfile
    generatedAt: str
    dataIsFixture: bool
    summary: PlanSummary
    options: List[PlanOption]
    timeline: List[TimelineItem]


class Fact(BaseModel):
    id: str
    label: str
    display: str
    kind: Literal["sourced", "calculated"]
    source: Optional[SourceRef] = None


class MentorAnswer(BaseModel):
    text: str
    rendered: str
    facts: List[Fact]
    usedFallback: bool


class PlanEnvelope(BaseModel):
    """Only `profile` is read from a plan sent by the browser; numbers are recalculated."""
    model_config = ConfigDict(extra="ignore")
    profile: StudentProfile


class ExplainRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    profile: Optional[StudentProfile] = None
    plan: Optional[PlanEnvelope] = None
    language: str = "en"

    @model_validator(mode="after")
    def _need_profile(self):
        if self.profile is None and self.plan is None:
            raise ValueError("profile is required (or a plan that contains its profile)")
        return self

    def student(self) -> StudentProfile:
        return self.profile or self.plan.profile


class ChatRequest(ExplainRequest):
    question: str = Field(min_length=1, max_length=4000)

    @model_validator(mode="after")
    def _need_question(self):
        if not self.question.strip():
            raise ValueError("question is required")
        return self


class SourceRow(BaseModel):
    field: str
    label: str
    value: Optional[Union[str, float, int, Dict[str, float]]] = None
    display: str
    published: bool
    source: Optional[SourceRef] = None


class UniversitySources(BaseModel):
    universityId: str
    universityName: str
    shortName: Optional[str] = None
    city: str
    sector: Optional[str] = None
    website: Optional[str] = None
    programId: str
    programName: str
    rows: List[SourceRow]


class SourcesResponse(BaseModel):
    dataIsFixture: bool
    universities: List[UniversitySources]


class Meta(BaseModel):
    groups: List[Dict[str, str]]
    cities: List[str]
    languages: List[Dict[str, str]]
    categories: List[Dict[str, str]]
    defaults: Dict[str, float]


class Health(BaseModel):
    status: Literal["ok"]
    dataset: Dict[str, Union[int, bool, List[str]]]
    mentor: Dict[str, Union[str, bool, None]]
