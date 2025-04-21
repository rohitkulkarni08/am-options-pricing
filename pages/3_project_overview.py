import streamlit as st # type: ignore

st.set_page_config(page_title="📘 Model Overview", page_icon="📚")
st.title("📘 American Options Pricing – Model Overview")

st.markdown("""
Welcome! This page explains how the American options pricing model was designed, trained, and deployed.
The goal is to predict realistic, non-negative option prices using structured financial features and deep learning.
""")

with st.expander("📌 Project Goal & Use Case", expanded=True):
    st.markdown("""
    This model powers an interactive chatbot to help users price American-style options.
    
    **User flow:**
    - 🧠 The user enters a natural-language query (e.g., "Price a call on AAPL expiring in 30 days")
    - 🤖 GPT extracts intent + structured fields
    - 🧮 The model uses 19 engineered features to predict the option price

    **Business value:**
    - Faster option pricing simulation
    - Explainability and education for retail traders
    - Extendable to forecasting or exercise probability
    """)

with st.expander("🗺️ End-to-End Model Flow", expanded=True):
    st.markdown("""
🧑‍💻 **User Query**  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
📥 **Prompt 1 (GPT Extraction + Intent)**  
- Extract Structured Data  
- Extract **Intent** (option_price_prediction / exercise_probability / forecasting)  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
📝 **Field Validator**  
- Validate extracted fields  
- Enrich / fill missing fields  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
🔀 **Intent Router**  
- Route request based on **Intent**  
- Call appropriate module  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
✅ **Redis Cache**  ➡️ (if hit, use it)  
✅ **BigQuery Check** ➡️ (fallback if Redis misses)  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
⚙️ **Feature Engineering**  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
🧠 **Module Processing (by Intent)**  
- Option Price Prediction  
- Exercise Probability  
- Forecasting  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
📥 **Prompt 2 (Follow-Up Prompt to GPT)**  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
🔮 **Model Prediction / Insights**  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
💬 **Chatbot Response**  
&nbsp;&nbsp;&nbsp;&nbsp;⬇️  
🧑‍💻 **User Receives Result + Suggestions**
    """)

with st.expander("🏗️ Model Architecture", expanded=True):
    st.markdown("""
    The model is a custom deep neural network with:

    - Gaussian noise input for robustness  
    - Feature-level attention layer  
    - Residual dense blocks for gradient flow  
    - BatchNorm + ELU activations  
    - Final softplus output to ensure non-negative prices  

    It’s compiled with **AdamW + cosine decay** and trained on **27 million rows** of options data.
    """)

with st.expander("🧾 Feature Set (19 Inputs)", expanded=False):
    st.markdown("""
    ```
    Sector, S0, K, T, sigma, r,
    moneyness, log_moneyness,
    RSI, MACD, Skewness, Kurtosis,
    delta, gamma, vega, theta, rho,
    early_exercise_prob, option_type
    ```
    These are fully numeric and encoded before being fed to the model.
    """)

with st.expander("⚙️ Training Details", expanded=False):
    st.markdown("""
    - **Data Size**: 27 million rows  
    - **Loss Function**: MSE  
    - **Metrics**: MAE  
    - **Batch Size**: 8192  
    - **Early Stopping** with patience = 10  
    - **ReduceLROnPlateau** to tune learning rate  
    - Saved as `.keras` file for clean deployment  
    """)

st.markdown("---")
st.info("Want to go deeper into predictions? Check the 'Explainability' page.")
st.success("This is a full-stack ML app — from language input to financial prediction, with explainability and deployment.")