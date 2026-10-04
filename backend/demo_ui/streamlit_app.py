"""Backup demo UI (Streamlit). Same engine and mentor as the API - no server needed.

    pip install -r backend/demo_ui/requirements.txt
    streamlit run backend/demo_ui/streamlit_app.py
"""
import streamlit as st

import _bootstrap

_bootstrap.load_secrets(st)

from data.loader import is_fixture, load_data  # noqa: E402
from engine.orchestrator import build_plan  # noqa: E402
from mentor import run_chat, run_explain  # noqa: E402

st.set_page_config(page_title="Rehnuma", page_icon="🎓", layout="wide")

st.title("🎓 Rehnuma")
st.caption("Your marks + budget + city → a transparent university plan.")

data = load_data()
if is_fixture(data):
    st.warning(
        "**Demo data.** The universities, fees and merits shown here are placeholders, not real figures. "
        "Replace `backend/data/*.json` with the verified dataset before presenting real results."
    )
st.info("Rehnuma's engine calculates every number from the dataset. The AI mentor only explains the finished plan.")

GROUPS = ["pre-engineering", "ics", "pre-medical", "icom", "fa"]
LANGUAGES = {"English": "en", "Roman Urdu": "roman-ur"}
BADGE = {"safe": "🟢 Safe", "target": "🟡 Target", "reach": "🟠 Reach", "unlikely": "🔴 Unlikely",
         "no-data": "⚪ No data", "not-eligible": "⛔ Not eligible"}

with st.sidebar:
    st.header("Student profile")
    matric_obtained = st.number_input("Matric marks obtained", min_value=0.0, value=1020.0)
    matric_total = st.number_input("Matric total", min_value=1.0, value=1100.0)
    inter_status = st.selectbox("Inter status", ["complete", "part1"])
    inter_obtained = st.number_input("Inter marks obtained", min_value=0.0, value=940.0)
    inter_total = st.number_input("Inter total", min_value=1.0, value=1100.0,
                                  help="Use 550 if you only have Part 1 marks.")
    group = st.selectbox("Group", GROUPS, index=1)
    home_city = st.text_input("Home city", value="Lahore")
    willing_to_relocate = st.checkbox("Willing to relocate", value=True)
    budget = st.number_input("Total budget for the degree (PKR)", min_value=0.0, value=1500000.0, step=50000.0)
    income = st.number_input("Family monthly income (optional, PKR)", min_value=0.0, value=0.0, step=5000.0,
                             help="Leave at 0 if you prefer not to say.")
    use_test = st.checkbox("I have an expected entry-test score", value=False)
    expected_test = st.number_input("Expected entry-test score %", min_value=0.0, max_value=100.0, value=70.0,
                                    disabled=not use_test)
    language = LANGUAGES[st.selectbox("Mentor language", list(LANGUAGES))]
    submitted = st.button("Build my plan", type="primary", width="stretch")

if submitted:
    errors = []
    if matric_obtained > matric_total:
        errors.append("Matric obtained cannot be more than the total.")
    if inter_obtained > inter_total:
        errors.append("Inter obtained cannot be more than the total.")
    if not home_city.strip():
        errors.append("Please enter your home city.")
    if errors:
        for message in errors:
            st.error(message)
        st.stop()

    profile = {
        "matricObtained": matric_obtained, "matricTotal": matric_total,
        "interObtained": inter_obtained, "interTotal": inter_total, "interStatus": inter_status,
        "group": group, "homeCity": home_city.strip(), "willingToRelocate": willing_to_relocate,
        "budgetTotal": budget, "familyIncomeMonthly": income if income > 0 else None,
        "expectedTestPercent": expected_test if use_test else None,
    }
    with st.spinner("Running Rehnuma agents..."):
        st.session_state["plan"] = build_plan(profile, data)
    st.session_state.pop("explanation", None)

if "plan" not in st.session_state:
    st.subheader("How it works")
    cols = st.columns(4)
    cols[0].metric("1", "Eligibility")
    cols[1].metric("2", "Aggregate + category")
    cols[2].metric("3", "Budget + scholarships")
    cols[3].metric("4", "Timeline + QA")
    st.write("Fill in the profile on the left and press **Build my plan**.")
    st.stop()

plan = st.session_state["plan"]


def show_answer(answer):
    st.write(answer["rendered"])
    sourced = [f for f in answer["facts"] if f["source"]]
    if sourced:
        st.caption(" · ".join(f"[{f['display']}]({f['source']['sourceUrl']})" for f in sourced) + " — sources")
    if answer["usedFallback"]:
        st.caption("Template answer (the AI model was not used for this reply).")


st.subheader("Your university plan")
summary = plan["summary"]
cols = st.columns(4)
cols[0].metric("Safe", summary["safe"])
cols[1].metric("Target", summary["target"])
cols[2].metric("Reach", summary["reach"])
cols[3].metric("Within budget", summary["withinBudget"])
st.caption("Categories are rule-based comparisons with last year's closing merit, not admission predictions.")

if plan["profile"]["interStatus"] == "part1":
    st.caption("Based on Part 1 marks.")
if not plan["options"]:
    st.warning("No university in our verified list is in your city. Turn on 'willing to relocate' to see more.")

for option in plan["options"]:
    with st.container(border=True):
        top = st.columns([3, 1, 1, 1])
        top[0].subheader(f"{option['universityName']} — {option['programName']}")
        top[1].write(f"**{BADGE[option['category']]}**")
        top[2].write(f"**City:** {option['city']}")
        top[3].write("**Budget:** " + ("within" if option["cost"]["withinBudget"] else "over"))
        st.write(option["categoryReason"])

        dash = lambda value, suffix="": "—" if value is None else f"{value}{suffix}"
        metrics = st.columns(5)
        metrics[0].metric("Matric %", option["matricPercent"])
        metrics[1].metric("Inter %", option["interPercent"])
        metrics[2].metric("Academic part", dash(option["academicPart"]))
        metrics[3].metric(f"Needed in {option['testName']}", dash(option["requiredTestPercent"], "%"))
        metrics[4].metric("Aggregate", dash(option["aggregate"]))

        cost = option["cost"]
        gap = f"PKR {abs(cost['gap']):,.0f} " + ("over budget" if cost["gap"] > 0 else "under budget")
        st.write(
            f"**Whole-degree cost:** PKR {cost['total']:,.0f} "
            f"(tuition {cost['tuition']:,.0f} + admission {cost['admissionFee']:,.0f} + hostel {cost['hostel']:,.0f}) "
            f"| **{gap}**"
        )
        if cost["hostelUnknown"]:
            st.warning("Hostel cost is not officially published, so it is not included in the total.")
        st.caption("Calculated at current fees. Fees can rise each year.")

        if option["scholarships"]:
            st.write("**Scholarships you can check** (not subtracted from the cost):")
            for scholarship in option["scholarships"]:
                st.write(f"- {scholarship['name']}: {scholarship['summary']} — [Apply]({scholarship['applyUrl']})")
        elif option["eligible"]:
            st.write("No matching scholarships in the current dataset.")

        if option["nextDeadline"]:
            deadline = option["nextDeadline"]
            st.write(f"**Next deadline:** {deadline['label']} — {deadline['date']} ({deadline['cycle']})")

        with st.expander("Sources"):
            for field, ref in option["sources"].items():
                st.write(
                    f"**{field}:** {ref['sourceName']} | verified {ref['verifiedOn']} | "
                    f"{ref['confidence']} | [open source]({ref['sourceUrl']})"
                )
            missing = [f for f in ("weights", "closingMerit", "hostelPerYear") if f not in option["sources"]]
            if missing:
                st.write("Not officially published: " + ", ".join(missing))

st.divider()
st.subheader("Admission timeline")
if plan["timeline"]:
    for item in plan["timeline"]:
        st.write(
            f"**{item['date']}** — {item['label']} — {item['universityName']} "
            f"({'past' if item['isPast'] else 'upcoming'})"
        )
else:
    st.write("No deadlines are available for your options.")

st.divider()
st.subheader("🤖 Rehnuma AI mentor")
st.caption("The mentor can only quote numbers from your plan. Without an API key it uses a safe template answer.")

if st.button("Explain my plan"):
    with st.spinner("Preparing explanation..."):
        st.session_state["explanation"] = run_explain(plan, language)
if "explanation" in st.session_state:
    show_answer(st.session_state["explanation"])

with st.form("ask", clear_on_submit=False):
    question = st.text_input("Ask a question about this plan", placeholder="Which option is best for my budget?")
    asked = st.form_submit_button("Ask the mentor")
if asked and question.strip():
    with st.spinner("Answering..."):
        show_answer(run_chat(plan, language, question))

with st.expander("How we decide"):
    st.markdown("""
- **Safe:** test score needed ≤ 60%, or (with an expected test score) aggregate at least 3 points above last closing merit.
- **Target:** needed > 60% and ≤ 75%, or aggregate from 2 points below to under 3 points above.
- **Reach:** needed > 75% and ≤ 90%, or aggregate from 7 points below to under 2 points below.
- **Unlikely:** needed > 90%, or aggregate more than 7 points below.
- Missing formula or closing merit → **No data**. Wrong group or below the minimum inter % → **Not eligible**.
- Scholarships are listed, never subtracted from the cost.
""")
