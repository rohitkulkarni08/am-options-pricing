from chatbot_controller import process_chatbot_request

def chatbot_loop():
    print("💬 Welcome to the American Option Pricing Chatbot! Type 'exit' to quit.\n")

    while True:
        user_query = input("You: ")
        if user_query.lower() == "exit":
            print("👋 Goodbye!")
            break

        response = process_chatbot_request(user_query)

        if 'error' in response:
            print(f"⚠️ Error: {response['error']}")
            continue

        print(f"\n📈 Stock: {response['ticker']}")
        print(f"💰 Latest Price: {response['latest_price']}")
        print(f"💵 Risk-Free Rate: {response['risk_free_rate']:.2%}")
        print(f"📝 Follow-up Suggestions:\n{response['follow_up']}")

if __name__ == "__main__":
    chatbot_loop()

# New
from chatbot.chatbot_controller import process_user_query

def chatbot_response(user_query: str):
    response = process_user_query(user_query)

    if "error" in response:
        return f"⚠️ Error: {response['error']}\nDetails: {response.get('details', '')}"
    
    return response.get("result")

if __name__ == "__main__":
    print("🤖 American Options Pricing Chatbot 🤖")
    while True:
        user_input = input("Ask me: ")
        reply = chatbot_response(user_input)
        print("🤖:", reply)
