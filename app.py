import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

# PDF dependencies
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import reportlab.lib.colors as rl_colors

# Project imports
from reactor.kinetics import simulate_transient
from reactor.transients import step_reactivity_insertion, load_following
from reactor.parameters import REACTOR_TYPES

from grid.dispatch import merit_order_dispatch

from scenarios.drought import apply_drought
from scenarios.nuclear_outage import simulate_outage
from planning.long_term import long_term_plan

st.set_page_config(
    page_title="NRGS Kenya — Nuclear & Renewable Grid Simulator",
    layout="wide",
    page_icon="🇰🇪",
    initial_sidebar_state="expanded"
)

# ─── PDF Report Generator ───
def generate_pdf_report(scenario_name, dispatch_df=None, extra_metrics=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"NRGS Scenario Report — {scenario_name}", styles['Title']))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M EAT')}", styles['Normal']))
    story.append(Paragraph("Nuclear & Renewable Grid Simulator • Kenya", styles['Normal']))
    story.append(Spacer(1, 24))

    if extra_metrics:
        story.append(Paragraph("Key Metrics", styles['Heading2']))
        data = [[k, v] for k, v in extra_metrics.items()]
        tbl = Table(data, colWidths=[220, 220])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rl_colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), rl_colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, rl_colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 24))

    if dispatch_df is not None:
        story.append(Paragraph("Dispatch Summary (First 12 hours + Totals)", styles['Heading2']))
        numeric_df = dispatch_df.select_dtypes(include='number').head(12)
        totals = numeric_df.sum().to_frame().T
        totals.index = ['Total (MWh)']
        summary = pd.concat([numeric_df, totals])

        data = [summary.columns.tolist()] + summary.round(1).values.tolist()
        tbl = Table(data)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), rl_colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, rl_colors.black),
        ]))
        story.append(tbl)

    doc.build(story)
    buffer.seek(0)
    return buffer

# ─── SIDEBAR ───
st.sidebar.title("NRGS 🇰🇪")
st.sidebar.markdown("**Nuclear & Renewable Grid Simulator**")

page = st.sidebar.radio(
    "Navigate",
    options=[
        "🏠 Home",
        "⚛️ Reactor Physics",
        "🌐 Grid Dispatch",
        "⚠️ Scenarios",
        "📈 Long-term Planning"
    ],
    index=0
)

with st.sidebar.expander("About NRGS"):
    st.markdown("""
    **Nuclear & Renewable Grid Simulator**  
    • Point-kinetics reactor transients  
    • Kenya merit-order grid dispatch  
    • Drought & nuclear outage scenarios  
    • Long-term planning outlook  
    Built for educational & planning purposes  
    Contact: **allinmer57@gmail.com**
    """)

# ─── HOME ─── (image restored)
if page == "🏠 Home":
    st.title("🇰🇪 Nuclear & Renewable Grid Simulator (NRGS)")
    st.markdown("**v2.1 MVP** — Supporting Kenya's clean energy transition")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
        ### What NRGS does
        - Simulates nuclear reactor transients (6-group kinetics + feedback)  
        - Models Kenya's grid dispatch (geothermal, hydro, wind, solar, thermal + nuclear)  
        - Tests resilience under drought and nuclear outage  
        - Shows long-term demand & capacity outlook  
        
        Uses real data from **EPRA**, **KenGen**, **LCPDP** and IAEA benchmarks.
        """)

    with col2:
       st.image(
    "https://raw.githubusercontent.com/wiseman-s/nuclear-renewable-grid-simulator/main/img%201.jpg",
    caption="NRGS Kenya – Visualizing nuclear & renewable integration in the grid",
    use_column_width=True
)

    st.divider()
    st.subheader("Key Benefits")
    cols = st.columns(4)
    cols[0].metric("Baseload Stability", "+35–45%", "Nuclear 24/7")
    cols[1].metric("CO₂ Reduction", "–30–45%", "vs thermal")
    cols[2].metric("Drought Resilience", "+55–70%", "less hydro stress")
    cols[3].metric("Cost Savings", "–12–25%", "hybrid mix")

    st.info("Purely computational → safe, educational, policy-oriented.")

# ─── REACTOR PHYSICS ───
elif page == "⚛️ Reactor Physics":
    st.header("⚛️ Reactor Transient Simulation")
    st.caption("6-group point kinetics + thermal feedback")

    col1, col2 = st.columns([3, 2])
    with col1:
        reactor_type = st.selectbox("Reactor Type", list(REACTOR_TYPES.keys()), index=1)
        scenario = st.selectbox("Transient", ["Step Reactivity Insertion", "Load Following"])

        if scenario == "Step Reactivity Insertion":
            rho = st.slider("ρ step ($)", 0.001, 0.015, 0.005, step=0.0005)
            t_ins = st.slider("Insert at (s)", 1, 10, 5)
            result = step_reactivity_insertion(rho_step=rho, t_insert=t_ins, reactor_type=reactor_type)
        else:
            target = st.slider("Target ratio", 0.5, 1.2, 0.8, 0.05)
            ramp = st.slider("Ramp time (s)", 10, 60, 30)
            result = load_following(target_power_ratio=target, ramp_time=ramp, reactor_type=reactor_type)

    with col2:
        st.metric("Type", reactor_type)
        overshoot = (result["P"].max() - 1) * 100 if result["P"].max() > 1 else 0
        st.metric("Peak Overshoot", f"{overshoot:.1f}%")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=result["t"], y=result["P"], name="Power", line=dict(color="#00CC96", width=3)))
    fig.add_trace(go.Scatter(x=result["t"], y=result["rho_ext"]*100, name="Ext ρ", yaxis="y2", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=result["t"], y=result["rho_fb"]*100, name="Feedback ρ", yaxis="y2", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=result["t"], y=result["rho_total"]*100, name="Total ρ", yaxis="y2", line=dict(color="red")))

    fig.update_layout(
        title="Power & Reactivity",
        xaxis_title="Time (s)",
        yaxis_title="Normalized Power",
        yaxis2=dict(title="Reactivity (cents)", overlaying="y", side="right", showgrid=False),
        height=550,
        legend=dict(orientation="h", y=1.02, x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── GRID DISPATCH ───
elif page == "🌐 Grid Dispatch":
    st.header("24-Hour Merit-Order Dispatch")

    include_nuc = st.checkbox("Include 1 GW Nuclear", value=True)

    demand_df = pd.read_csv('data/kenya_load_profile.csv')
    demand = demand_df['load_mw'].values

    dispatch_df = merit_order_dispatch(demand_profile=demand, include_nuclear=include_nuc)

    source_colors = {
        'nuclear': '#636EFA', 'geothermal': '#00CC96', 'hydro': '#1F77B4',
        'wind': '#FF7F0E', 'solar': '#FFD700', 'thermal': '#D62728', 'unserved_mw': '#FF4444'
    }

    fig = go.Figure()
    numeric_cols = dispatch_df.select_dtypes(include='number').columns

    for col in numeric_cols:
        if col == 'unserved_mw': continue
        if dispatch_df[col].sum() > 0:
            fig.add_trace(go.Bar(x=dispatch_df.index, y=dispatch_df[col],
                                 name=col.capitalize(), marker_color=source_colors.get(col, '#AAAAAA')))

    if 'unserved_mw' in dispatch_df.columns and dispatch_df['unserved_mw'].sum() > 0:
        fig.add_trace(go.Bar(x=dispatch_df.index, y=dispatch_df['unserved_mw'],
                             name='Unserved', marker_color=source_colors['unserved_mw'], opacity=0.85))

    fig.update_layout(barmode='stack', title="Hourly Dispatch", xaxis_title="Hour", yaxis_title="MW",
                      height=550, legend=dict(orientation="h", y=1.02, x=1))
    st.plotly_chart(fig, use_container_width=True)

    total_mwh = dispatch_df.select_dtypes('number').sum().sum()
    unserved_mwh = dispatch_df.get('unserved_mw', pd.Series(0)).sum()
    unserved_pct = (unserved_mwh / (total_mwh + unserved_mwh)) * 100 if total_mwh > 0 else 0

    cols = st.columns(3)
    cols[0].metric("Total Dispatched", f"{total_mwh:,.0f} MWh")
    cols[1].metric("Unserved Energy", f"{unserved_mwh:,.0f} MWh")
    cols[2].metric("Unserved %", f"{unserved_pct:.2f}%", delta_color="inverse")

    st.markdown("""
    **Explanation of metrics:**
    - **Total Dispatched** — Total electricity supplied over 24 hours (equals total demand if no unserved energy)
    - **Unserved Energy** — Electricity demand that could not be met (0 means the grid fully supplied the load)
    - **Unserved %** — Percentage of demand not served (0% = perfect reliability in this simulation)
    """)

    numeric_disp = dispatch_df.select_dtypes('number')
    st.dataframe(numeric_disp.style.format("{:,.0f}"), use_container_width=True)

    if st.button("Export Grid Report (PDF)"):
        metrics = {
            "Nuclear Included": "Yes" if include_nuc else "No",
            "Total Dispatched (MWh)": f"{total_mwh:,.0f}",
            "Unserved (MWh)": f"{unserved_mwh:,.0f}",
            "Unserved (%)": f"{unserved_pct:.2f}"
        }
        pdf = generate_pdf_report("Current Grid Dispatch", dispatch_df, metrics)
        st.download_button(
            "Download PDF",
            pdf,
            f"NRGS_Grid_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            "application/pdf"
        )

# ─── SCENARIOS ───
elif page == "⚠️ Scenarios":
    st.header("Stress Test Scenarios")

    scenario = st.selectbox("Scenario", [
        "Baseline (Current Mix + Nuclear)",
        "Moderate Drought (Hydro -35%)",
        "Severe Drought (Hydro -60%)",
        "Nuclear Unit Outage (24 hours)"
    ])

    demand = pd.read_csv('data/kenya_load_profile.csv')['load_mw'].values

    if "Moderate" in scenario:
        dispatch_df = apply_drought(demand, "moderate")
    elif "Severe" in scenario:
        dispatch_df = apply_drought(demand, "severe")
    elif "Nuclear" in scenario:
        dispatch_df = simulate_outage(demand)
    else:
        dispatch_df = merit_order_dispatch(demand, include_nuclear=True)

    source_colors = {
        'nuclear': '#636EFA', 'geothermal': '#00CC96', 'hydro': '#1F77B4',
        'wind': '#FF7F0E', 'solar': '#FFD700', 'thermal': '#D62728', 'unserved_mw': '#FF4444'
    }

    fig = go.Figure()
    numeric_cols = dispatch_df.select_dtypes(include='number').columns

    for col in numeric_cols:
        if col == 'unserved_mw': continue
        if dispatch_df[col].sum() > 0:
            fig.add_trace(go.Bar(x=dispatch_df.index, y=dispatch_df[col],
                                 name=col.capitalize(), marker_color=source_colors.get(col, '#AAAAAA')))

    if 'unserved_mw' in dispatch_df.columns and dispatch_df['unserved_mw'].sum() > 0:
        fig.add_trace(go.Bar(x=dispatch_df.index, y=dispatch_df['unserved_mw'],
                             name='Unserved', marker_color=source_colors['unserved_mw'], opacity=0.85))

    fig.update_layout(barmode='stack', title=f"{scenario}", xaxis_title="Hour", yaxis_title="MW",
                      height=550, legend=dict(orientation="h", y=1.02, x=1))
    st.plotly_chart(fig, use_container_width=True)

    total_mwh = dispatch_df.select_dtypes('number').sum().sum()
    unserved_mwh = dispatch_df.get('unserved_mw', pd.Series(0)).sum()
    unserved_pct = (unserved_mwh / (total_mwh + unserved_mwh)) * 100 if total_mwh > 0 else 0

    cols = st.columns(3)
    cols[0].metric("Total Dispatched", f"{total_mwh:,.0f} MWh")
    cols[1].metric("Unserved Energy", f"{unserved_mwh:,.0f} MWh")
    cols[2].metric("Unserved %", f"{unserved_pct:.2f}%", delta_color="inverse")

    st.markdown("""
    **Explanation of metrics:**
    - **Total Dispatched** — Total electricity supplied over 24 hours (equals total demand if no unserved energy)
    - **Unserved Energy** — Electricity demand that could not be met (0 means the grid fully supplied the load)
    - **Unserved %** — Percentage of demand not served (0% = perfect reliability in this simulation)
    """)

    numeric_disp = dispatch_df.select_dtypes('number')
    st.dataframe(numeric_disp.style.format("{:,.0f}"), use_container_width=True)

    if st.button("Export Scenario Report (PDF)"):
        metrics = {
            "Scenario": scenario,
            "Total Dispatched (MWh)": f"{total_mwh:,.0f}",
            "Unserved (MWh)": f"{unserved_mwh:,.0f}",
            "Unserved (%)": f"{unserved_pct:.2f}"
        }
        pdf = generate_pdf_report(scenario, dispatch_df, metrics)
        fname = f"NRGS_{scenario.replace(' ','_').replace('(','').replace(')','')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        st.download_button("Download PDF Report", pdf, file_name=fname, mime="application/pdf")

# ─── LONG-TERM PLANNING ───
elif page == "📈 Long-term Planning":
    st.header("2030–2040 Outlook")

    years = st.slider("Horizon (years)", 10, 20, 15)
    growth = st.slider("Annual demand growth (%)", 3.0, 7.0, 4.5, 0.5) / 100
    nuc_year = st.slider("Nuclear online after (years)", 5, 12, 8)

    plan_df = long_term_plan(years=years, annual_growth=growth, nuclear_commission_year=nuc_year)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plan_df['year'], y=plan_df['peak_demand_mw'], name='Peak Demand', line=dict(color='#1F77B4', width=3)))
    fig.add_trace(go.Scatter(x=plan_df['year'], y=plan_df['nuclear_capacity_mw'], name='Nuclear', fill='tozeroy', fillcolor='rgba(99,110,250,0.3)'))
    fig.update_layout(title="Demand vs Nuclear Capacity", xaxis_title="Year", yaxis_title="MW", height=550)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(plan_df.style.format(precision=0, thousands=","), use_container_width=True)

# ─── FOOTER ───
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: grey; font-size: 0.9em;'>"
    "System developed by Simon • Contact: allinmer57@gmail.com"
    "</p>",
    unsafe_allow_html=True
)
