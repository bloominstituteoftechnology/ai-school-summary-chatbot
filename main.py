from chatbot import SummarizingChatBot

def chat_with_bot():
    print("Chat with the bot (type 'exit' to stop):")
    summarizing_chatbot = SummarizingChatBot()
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = summarizing_chatbot.get_response(user_input)
        print(f"Bot: {response}")

if __name__ == "__main__":
    chat_with_bot()