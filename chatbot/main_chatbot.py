from chatbot_controller import process_chatbot_request

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
