from chatbot.chatbot_utils import extract_intent_and_entities
from chatbot.validator import validate_fields
from chatbot.intent_router import route_intent

def process_user_query(user_query: str):
    extraction_result = extract_intent_and_entities(user_query)

    if "error" in extraction_result:
        return extraction_result

    intent = extraction_result.get('intent')
    entities = extraction_result.get('entities')

    validated_data, validation_errors = validate_fields(entities)

    if validation_errors:
        return {"error": "Validation failed", "details": validation_errors}

    result = route_intent(intent, validated_data)
    return result
