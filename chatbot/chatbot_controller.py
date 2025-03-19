from chatbot.chatbot_utils import extract_intent_and_entities
from chatbot.validator import validate_and_find_missing_fields
# from chatbot.intent_router import route_intent  # Not used yet

from ingestion_pipeline.caching import get_from_cache, set_cache
from ingestion_pipeline.database import query_bigquery_table, insert_into_bigquery
from ingestion_pipeline.data_fetch import fetch_missing_fields
from ingestion_pipeline.feature_engineering import engineer_features

def process_user_query(user_query: str):
    """
    Process user query by extracting intent, validating fields, 
    retrieving or enriching data, and returning the result.
    """
    # Step 1: Extract intent & entities from user query
    extraction_result = extract_intent_and_entities(user_query)

    if "error" in extraction_result:
        return extraction_result

    intent = extraction_result.get('intent')
    entities = extraction_result.get('entities')

    # Step 2: Validate extracted fields and find missing ones
    validated_data, missing_fields = validate_and_find_missing_fields(entities)

    # Step 3: Generate a unique cache key (based on validated_data)
    cache_key = generate_cache_key(validated_data)

    # Step 4: Check Redis cache first
    cached_result = get_from_cache(cache_key)
    if cached_result:
        print("Cache hit. Returning cached result.")
        return cached_result

    # Step 5: Query BigQuery next
    bq_result = query_bigquery_table(validated_data)
    if bq_result:
        print("Found in BigQuery. Returning result and caching it.")
        set_cache(cache_key, bq_result)
        return bq_result

    # Step 6: Fetch missing fields (external APIs or default calculations)
    if missing_fields:
        fetched_data = fetch_missing_fields(missing_fields, validated_data)
        validated_data.update(fetched_data)

    # Step 7: Perform feature engineering on the combined data
    engineered_data = engineer_features(validated_data)

    # Step 8: Save the engineered data for future queries
    insert_into_bigquery(engineered_data)
    set_cache(cache_key, engineered_data)

    # Step 9: Return the final engineered data (or defer to prediction later)
    return {
        "message": "Data processed and ready for prediction routing.",
        "engineered_data": engineered_data
    }

def generate_cache_key(validated_data):
    """
    Generate a unique Redis cache key based on key data fields.
    """
    key_parts = [
        validated_data.get('Ticker', 'unknown'),
        str(validated_data.get('K', 'unknown')),
        str(validated_data.get('S0', 'unknown')),
        str(validated_data.get('option_type', 'unknown'))
    ]
    return '|'.join(key_parts)
