import streamlit as st # type: ignore
from utils.gpt_interface import convert_markdown_headings_to_html, extract_intent_and_entities, generate_comprehensive_model_summary
from utils.input_validation import validate_and_find_missing_fields
from utils.data_fetch import fetch_from_bigquery, get_dynamic_start_date
from utils.data_loading import upload_to_bigquery
from ingestion_pipeline.feature_engineering import engineer_features
from ingestion_pipeline.greeks import prepare_model_input
import pandas as pd  # type: ignore
from predictions.exercise_probability import predict_prob_from_raw_df
from predictions.option_pricing import predict_price_with_shap
from datetime import datetime
from ingestion_pipeline.data_ingestion import get_stock_data, get_sector, add_shock_events

import warnings
warnings.filterwarnings("ignore")


st.set_page_config(page_title="Options Chatbot", page_icon="📈")
st.title("American Options Pricing Chatbot")

user_query = st.text_area("Enter your query:")
submit = st.button("Generate Response")

if submit and user_query:
    with st.spinner("Thinking..."):
        try:
            extraction_result = extract_intent_and_entities(user_query)

            entities = extraction_result.get('entities')
            intent = extraction_result.get("intent", "unknown")

            validated_data, missing = validate_and_find_missing_fields(entities)
            st.markdown("I have validated your query, presenting results shortly....")

            if missing:
                st.warning(f"Missing fields: {', '.join(missing)}")

                with st.form("fill_missing_form"):
                    st.subheader("✏️ Please fill in the missing fields")

                    for field in missing:
                        if field == "K":
                            validated_data["K"] = st.number_input("Strike Price (K)", min_value=0.0)
                        elif field == "option_type":
                            opt = st.selectbox("Option Type", ["Call", "Put"])
                            validated_data["option_type"] = 1 if opt == "Call" else 0
                        elif field == "expiry_date":
                            date = st.date_input("Expiry Date")
                            validated_data["expiry_date"] = date.isoformat()
                        elif field == "Ticker":
                            validated_data["Ticker"] = st.text_input("Ticker (e.g., AAPL)")

                    submit_missing = st.form_submit_button("Update & Continue")

                if not submit_missing:
                    st.stop()  # wait until user submits the missing fields

            ticker = validated_data["Ticker"]

            bq_df, needs_update, last_date = fetch_from_bigquery((validated_data, missing))
            if bq_df is None or needs_update:
                st.warning("Fetching missing records from Yahoo Finance...")
                start_date = get_dynamic_start_date(last_date)
                end_date = datetime.today().strftime("%Y-%m-%d")

                new_data = get_stock_data([ticker], start_date, end_date)

                if not new_data.empty:
                    new_data = add_shock_events(new_data)
                    new_data["Sector"] = new_data["Ticker"].apply(get_sector)

                    upload_to_bigquery(new_data)

                    #st.success("BigQuery updated with new records.")
                
                else:
                    st.error("No new data fetched.")
                    st.stop()
            else:
                engineered = engineer_features(bq_df)

                latest = engineered.sort_values("Date").iloc[-1:]
                
                final_df = prepare_model_input(latest, validated_data)

                final_df = final_df.convert_dtypes()

                nullable_fix_map = {
                    "Volume": "int64",
                    "Relative_Volume_20d": "float64",
                    "Volume_Change_1d": "float64",
                    "Volume_Change_5d": "float64",
                    "option_type": "int"
                }
                
                for col, dtype in nullable_fix_map.items():
                    if col in final_df.columns:
                        try:
                            final_df[col] = final_df[col].astype(dtype)
                        except Exception as e:
                            st.warning(f"Couldn't cast column {col} to {dtype}: {e}")

                option_price, shap_dict = predict_price_with_shap(final_df)
                summary = generate_comprehensive_model_summary(final_df.iloc[0].to_dict(), option_price, shap_dict)

                styled_summary = convert_markdown_headings_to_html(summary)
                styled_summary = styled_summary.replace('\n\n', '</p><p>').replace('\n', '<br>')
                
                st.markdown(f"""
                            <div style="text-align: justify; line-height: 1.6; font-size: 16px;">
                            <p>{styled_summary}</p>
                            </div>
                            """, unsafe_allow_html=True)

                st.session_state["final_df"] = final_df
                    
        except Exception as e:
            st.error(f"Something went wrong: {e}")