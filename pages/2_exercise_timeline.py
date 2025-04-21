import streamlit as st # type: ignore
from utils.simulations import simulate_and_plot_predictions
from utils.gpt_interface import generate_option_timeline_summary

st.set_page_config(page_title="Option Timeline", page_icon="📚")
st.subheader("📘 American Options Pricing - Timeline Overview")

st.markdown("""
This page explains how your options performsduring it's lifetime!!!!
""")

if "final_df" not in st.session_state:
    st.warning("Please make a prediction on the home page first.")
    st.stop()

final_df = st.session_state["final_df"]

st.sidebar.markdown("### Simulation Settings")
smooth = st.sidebar.toggle("Use Daily (Smooth) Simulation", value=False)
n_points = st.sidebar.slider("Number of Points (if not smooth)", min_value=3, max_value=20, value=5)

with st.spinner("Simulating price and exercise probability..."):
    df_result, fig = simulate_and_plot_predictions(
        df_row=final_df,
        smooth=smooth,
        n_points=n_points
    )
    summary = generate_option_timeline_summary(df_result)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### Option Timeline Summary")
st.markdown(summary)
