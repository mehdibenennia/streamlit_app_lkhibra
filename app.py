
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="AI Workshop Dashboard",
    page_icon="📊",
    layout="wide",
)

DEFAULT_FILE = "AI_Workshop_Example_Data.xlsx"


@st.cache_data
def load_data(source):
    """Load and clean the Inquiries sheet."""
    df = pd.read_excel(source, sheet_name="Inquiries", header=2)
    df = df.iloc[:, :10].copy()
    df.columns = [
        "Inquiry ID",
        "Inquiry date",
        "Week",
        "City",
        "Discovery channel",
        "Main interest",
        "Response hours",
        "Registered",
        "Attended",
        "Satisfaction /5",
    ]

    df["Inquiry date"] = pd.to_datetime(df["Inquiry date"], errors="coerce")
    df["Response hours"] = pd.to_numeric(df["Response hours"], errors="coerce")
    df["Satisfaction /5"] = pd.to_numeric(df["Satisfaction /5"], errors="coerce")
    df["Registered flag"] = df["Registered"].eq("Yes")
    df["Attended flag"] = df["Attended"].eq("Yes")
    return df


def pct(value):
    return f"{value:.1%}"


def channel_summary(df):
    g = df.groupby("Discovery channel", sort=False)
    out = g.agg(
        Inquiries=("Inquiry ID", "size"),
        Registered=("Registered flag", "sum"),
        Attended=("Attended flag", "sum"),
        Avg_response_hours=("Response hours", "mean"),
    ).reset_index()
    out["Inquiry_to_attendance"] = out["Attended"] / out["Inquiries"]
    out["Registration_rate"] = out["Registered"] / out["Inquiries"]
    return out.sort_values("Inquiries", ascending=False)


def interest_summary(df):
    g = df.groupby("Main interest", sort=False)
    out = g.agg(
        Inquiries=("Inquiry ID", "size"),
        Registered=("Registered flag", "sum"),
        Attended=("Attended flag", "sum"),
    ).reset_index()
    out["Inquiry_to_attendance"] = out["Attended"] / out["Inquiries"]
    return out.sort_values("Inquiries", ascending=False)


def weekly_summary(df):
    order = [f"Week {i}" for i in range(1, 7)]
    g = df.groupby("Week", sort=False)
    out = g.agg(
        Inquiries=("Inquiry ID", "size"),
        Registered=("Registered flag", "sum"),
        Attended=("Attended flag", "sum"),
    ).reindex(order).reset_index()
    return out


def fig_channel_counts(cs):
    fig, ax = plt.subplots(figsize=(8, 4))
    x = range(len(cs))
    ax.bar([i - 0.18 for i in x], cs["Inquiries"], width=0.36, label="Inquiries")
    ax.bar([i + 0.18 for i in x], cs["Attended"], width=0.36, label="Attended")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cs["Discovery channel"], rotation=20, ha="right")
    ax.set_ylabel("People")
    ax.set_title("Inquiries and attendees by channel")
    ax.legend()
    fig.tight_layout()
    return fig


def fig_channel_rates(cs):
    fig, ax = plt.subplots(figsize=(8, 4))
    rates = cs.sort_values("Inquiry_to_attendance", ascending=False)
    ax.bar(rates["Discovery channel"], rates["Inquiry_to_attendance"] * 100)
    ax.set_ylabel("Inquiry → attendance (%)")
    ax.set_title("Inquiry-to-attendance rate by channel")
    ax.tick_params(axis="x", rotation=20)
    for i, v in enumerate(rates["Inquiry_to_attendance"] * 100):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    fig.tight_layout()
    return fig


def fig_interests(ins):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(ins["Main interest"], ins["Inquiries"])
    ax.set_ylabel("Inquiries")
    ax.set_title("Most requested topics")
    ax.tick_params(axis="x", rotation=15)
    for i, v in enumerate(ins["Inquiries"]):
        ax.text(i, v + 2, str(v), ha="center", fontsize=9)
    fig.tight_layout()
    return fig


def fig_response(cs):
    rates = cs.sort_values("Avg_response_hours")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(rates["Discovery channel"], rates["Avg_response_hours"])
    ax.set_ylabel("Average response time (hours)")
    ax.set_title("Average response time by channel")
    ax.tick_params(axis="x", rotation=20)
    for i, v in enumerate(rates["Avg_response_hours"]):
        ax.text(i, v + 0.6, f"{v:.1f}h", ha="center", fontsize=9)
    fig.tight_layout()
    return fig


def fig_weekly(ws):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(ws["Week"], ws["Inquiries"], marker="o", label="Inquiries")
    ax.plot(ws["Week"], ws["Registered"], marker="o", label="Registered")
    ax.plot(ws["Week"], ws["Attended"], marker="o", label="Attended")
    ax.set_ylabel("People")
    ax.set_title("Six-week workshop funnel")
    ax.legend()
    fig.tight_layout()
    return fig


# ---------- Sidebar / data source ----------
st.sidebar.title("AI Workshop Dashboard")
st.sidebar.caption("Built with Streamlit + pandas + matplotlib")

uploaded = st.sidebar.file_uploader(
    "Upload the Excel workbook",
    type=["xlsx"],
    help="Use AI_Workshop_Example_Data.xlsx or another workbook with the same sheet structure.",
)

if uploaded is not None:
    df = load_data(uploaded)
elif Path(DEFAULT_FILE).exists():
    df = load_data(DEFAULT_FILE)
else:
    st.title("AI Workshop Dashboard")
    st.warning(
        f"Upload `{DEFAULT_FILE}` in the sidebar to start. "
        "The app expects an `Inquiries` sheet with the workbook's standard columns."
    )
    st.stop()

cs = channel_summary(df)
ins = interest_summary(df)
ws = weekly_summary(df)

# ---------- Navigation ----------
page = st.sidebar.radio(
    "Page",
    ["1. Answers & Executive Summary", "2. Interactive Dashboard", "3. Data & Methodology"],
)

# ---------- Page 1 ----------
if page == "1. Answers & Executive Summary":
    st.title("AI Workshop — Answers to the six questions")
    st.caption(
        f"Analysis of {len(df):,} fictional inquiries from "
        f"{df['Inquiry date'].min():%d %b %Y} to {df['Inquiry date'].max():%d %b %Y}."
    )

    total = len(df)
    registered = int(df["Registered flag"].sum())
    attended = int(df["Attended flag"].sum())
    attendance_rate = attended / total if total else 0
    avg_sat = df.loc[df["Attended flag"], "Satisfaction /5"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inquiries", f"{total:,}")
    c2.metric("Registered", f"{registered:,}", f"{registered / total:.1%} of inquiries")
    c3.metric("Attended", f"{attended:,}", f"{attendance_rate:.1%} of inquiries")
    c4.metric("Avg. satisfaction", f"{avg_sat:.1f}/5")

    st.divider()

    # Q1
    st.subheader("1. Which channel brought the most inquiries?")
    top_q1 = cs.iloc[0]
    st.write(
        f"**{top_q1['Discovery channel']}** brought the most inquiries: "
        f"**{int(top_q1['Inquiries'])}** ({top_q1['Inquiries']/total:.1%} of all inquiries)."
    )
    st.dataframe(
        cs[["Discovery channel", "Inquiries"]].rename(columns={"Discovery channel": "Channel"}),
        use_container_width=True,
        hide_index=True,
    )

    # Q2
    st.subheader("2. Which channel brought the most attendees?")
    max_att = cs["Attended"].max()
    top_att = cs[cs["Attended"] == max_att]["Discovery channel"].tolist()
    names = ", ".join(top_att)
    st.write(
        f"**{names}** brought the most attendees, with **{int(max_att)} each**. "
        "The inquiry-to-attendance rate is a different measure and should be considered separately."
    )
    q2 = cs[["Discovery channel", "Inquiries", "Attended", "Inquiry_to_attendance"]].copy()
    q2["Inquiry_to_attendance"] = q2["Inquiry_to_attendance"].map(pct)
    q2.columns = ["Channel", "Inquiries", "Attended", "Inquiry → attendance"]
    st.dataframe(q2, use_container_width=True, hide_index=True)

    # Q3
    st.subheader("3. What topic is most requested?")
    top_interest = ins.iloc[0]
    st.write(
        f"**{top_interest['Main interest']}** is the most requested topic, with "
        f"**{int(top_interest['Inquiries'])} inquiries** ({top_interest['Inquiries']/total:.1%}). "
        "It represents a substantially larger share of demand than the other listed interests."
    )
    q3 = ins[["Main interest", "Inquiries", "Registered", "Attended"]].copy()
    q3.columns = ["Interest", "Inquiries", "Registered", "Attended"]
    st.dataframe(q3, use_container_width=True, hide_index=True)

    # Q4
    st.subheader("4. Does reply speed differ by channel?")
    fastest = cs.sort_values("Avg_response_hours").iloc[0]
    slowest = cs.sort_values("Avg_response_hours", ascending=False).iloc[0]
    st.write(
        f"Yes. Average response time varies across channels: **{fastest['Discovery channel']}** "
        f"is fastest at **{fastest['Avg_response_hours']:.1f} hours**, while "
        f"**{slowest['Discovery channel']}** is slowest at **{slowest['Avg_response_hours']:.1f} hours**. "
        "These are descriptive differences; the data does not establish that response speed causes registration or attendance."
    )
    q4 = cs[["Discovery channel", "Avg_response_hours"]].copy()
    q4["Avg_response_hours"] = q4["Avg_response_hours"].round(1)
    q4.columns = ["Channel", "Average response hours"]
    st.dataframe(q4, use_container_width=True, hide_index=True)

    # Q5
    st.subheader("5. How did inquiries change over six weeks?")
    first = ws.iloc[0]["Inquiries"]
    last = ws.iloc[-1]["Inquiries"]
    peak = ws.loc[ws["Inquiries"].idxmax()]
    st.write(
        f"Inquiries moved from **{int(first)} in Week 1** to **{int(last)} in Week 6**. "
        f"The peak was **Week {peak['Week'].split()[-1]} with {int(peak['Inquiries'])} inquiries**. "
        "The final week is lower than the peak and also has fewer attendees."
    )
    st.dataframe(ws, use_container_width=True, hide_index=True)
    st.pyplot(fig_weekly(ws), use_container_width=True)

    # Q6
    st.subheader("6. What should the team do next?")
    st.markdown(
        """
**One-page action report**

**Situation.** The workshop generated 300 inquiries, 176 registrations, and 130 attendees.
The strongest inquiry volume came from Instagram, while Referrals had the highest
inquiry-to-attendance rate among the channels in the dataset. Create a website was the
largest stated learning interest.

**What to do next.**
1. **Protect volume:** continue measuring Instagram because it generated the largest inquiry volume.
2. **Study high-performing acquisition:** examine what is happening in Referrals and Website, especially their conversion and attendance patterns.
3. **Prioritize demand:** make “Create a website” a prominent workshop/message theme because it is the largest interest group.
4. **Improve follow-up operations:** response times differ materially by channel; review the slower channels and test a faster response process.
5. **Watch the weekly funnel:** Week 6 had fewer inquiries and attendees than the peak week, so monitor whether this persists in future cohorts.
6. **Keep measurement disciplined:** track inquiries → registrations → attendance by channel and week, and continue recording response time and satisfaction.

These recommendations are operational next steps based on the descriptive dataset; they do not establish causal effects.
"""
    )

    st.markdown("**Five-slide presentation outline**")
    slides = {
        "Slide 1 — Executive snapshot": "300 inquiries → 176 registrations → 130 attendees; average attendee satisfaction: 4.2/5.",
        "Slide 2 — Acquisition channels": "Instagram led inquiry volume. Instagram and Website each produced 37 attendees. Referrals had the highest inquiry-to-attendance rate.",
        "Slide 3 — What people want": "Create a website was the largest interest category with 139 inquiries, followed by Organize work (101) and Office tools (60).",
        "Slide 4 — Response & weekly trend": "Average response time differed by channel. Weekly inquiries peaked in Week 3 at 56 and fell to 42 in Week 6.",
        "Slide 5 — Next actions": "Maintain volume channels, study high-attendance channels, emphasize the strongest topic, improve response operations, and monitor the weekly funnel.",
    }
    for title, body in slides.items():
        st.markdown(f"**{title}**")
        st.write(body)

# ---------- Page 2 ----------
elif page == "2. Interactive Dashboard":
    st.title("Interactive Workshop Dashboard")

    with st.sidebar.expander("Filters", expanded=True):
        selected_weeks = st.multiselect(
            "Week",
            options=[f"Week {i}" for i in range(1, 7)],
            default=[f"Week {i}" for i in range(1, 7)],
        )
        selected_channels = st.multiselect(
            "Discovery channel",
            options=sorted(df["Discovery channel"].dropna().unique()),
            default=sorted(df["Discovery channel"].dropna().unique()),
        )
        selected_interests = st.multiselect(
            "Main interest",
            options=sorted(df["Main interest"].dropna().unique()),
            default=sorted(df["Main interest"].dropna().unique()),
        )

    filtered = df[
        df["Week"].isin(selected_weeks)
        & df["Discovery channel"].isin(selected_channels)
        & df["Main interest"].isin(selected_interests)
    ].copy()

    f_registered = int(filtered["Registered flag"].sum())
    f_attended = int(filtered["Attended flag"].sum())
    f_total = len(filtered)

    a, b, c, d = st.columns(4)
    a.metric("Filtered inquiries", f"{f_total:,}")
    b.metric("Registered", f"{f_registered:,}")
    c.metric("Attended", f"{f_attended:,}")
    d.metric(
        "Inquiry → attendance",
        pct(f_attended / f_total) if f_total else "—",
    )

    if f_total == 0:
        st.info("No records match the selected filters.")
        st.stop()

    fcs = channel_summary(filtered)
    fins = interest_summary(filtered)
    fws = weekly_summary(filtered)

    left, right = st.columns(2)
    with left:
        st.pyplot(fig_channel_counts(fcs), use_container_width=True)
    with right:
        st.pyplot(fig_channel_rates(fcs), use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.pyplot(fig_interests(fins), use_container_width=True)
    with right:
        st.pyplot(fig_response(fcs), use_container_width=True)

    st.pyplot(fig_weekly(fws), use_container_width=True)

    st.subheader("Filtered channel performance")
    display_cs = fcs.copy()
    display_cs["Inquiry → attendance"] = display_cs["Inquiry_to_attendance"].map(pct)
    display_cs["Registration rate"] = display_cs["Registration_rate"].map(pct)
    display_cs["Avg response (hours)"] = display_cs["Avg_response_hours"].round(1)
    display_cs = display_cs[
        [
            "Discovery channel",
            "Inquiries",
            "Registered",
            "Attended",
            "Inquiry → attendance",
            "Registration rate",
            "Avg response (hours)",
        ]
    ]
    st.dataframe(display_cs, use_container_width=True, hide_index=True)

# ---------- Page 3 ----------
else:
    st.title("Data & Methodology")
    st.write(
        "The workbook contains fictional teaching data. No names or contact details are included."
    )

    st.subheader("Definitions")
    st.markdown(
        """
- **Inquiry-to-attendance rate** = attendees ÷ inquiries, as specified in the workbook.
- **Registration rate** = registered ÷ inquiries.
- **Attendance rate among registrants** = attendees ÷ registered.
- **Satisfaction** is recorded only for attendees.
- Differences in response time are descriptive and should not be interpreted as causal evidence.
- Small groups, such as Local event, should be interpreted cautiously because they contain relatively few inquiries.
"""
    )

    st.subheader("Data quality checks")
    checks = pd.DataFrame(
        {
            "Check": [
                "Attended without registering",
                "Missing response hours",
                "Missing satisfaction for attendees",
            ],
            "Result": [
                int((df["Attended flag"] & ~df["Registered flag"]).sum()),
                int(df["Response hours"].isna().sum()),
                int(df.loc[df["Attended flag"], "Satisfaction /5"].isna().sum()),
            ],
        }
    )
    st.dataframe(checks, use_container_width=True, hide_index=True)

    st.subheader("Raw data")
    st.dataframe(df.drop(columns=["Registered flag", "Attended flag"]), use_container_width=True, hide_index=True)
