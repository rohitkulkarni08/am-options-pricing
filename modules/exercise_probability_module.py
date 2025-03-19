def calculate_exercise_probability(validated_data: dict):
    underlying = validated_data['underlying_asset']

    # Placeholder logic
    probability = 0.75

    return {
        "result": f"The probability of early exercise for {underlying} is {probability * 100:.2f}%."
    }
