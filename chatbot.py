import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI class with the retrieved API key
client = OpenAI(api_key=api_key)

def generate_response(prompt, model="gpt-3.5-turbo"):
    """
    Generates a text response based on the given prompt and model.
    
    :param prompt: The input string for the AI model to process.
    :param model: The model identifier to be used for generating the response.
    :return: A string containing the processed output from the AI model.
    """
    try:
        response = client.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def summarize_text(text, model="gpt-3.5-turbo"):
    """
    Summarizes the provided text using the specified AI model.
    
    :param text: The text to be summarized.
    :param model: The model identifier to use for summarization.
    :return: A summary of the input text.
    """
    summary_prompt = f"Summarize this conversation:\n{text}"
    return generate_response(summary_prompt, model)

def assess_complexity(history, model="gpt-3.5-turbo"):
    """
    Assesses the complexity of a conversation history and returns a complexity score.
    
    :param history: A list of strings representing the conversation history.
    :param model: The model identifier to use for assessing complexity.
    :return: An integer representing the complexity score of the conversation.
    """
    complexity_prompt = f"Assess the complexity of this conversation:\n{' '.join(history)}\n\nComplexity Score:"
    complexity_text = generate_response(complexity_prompt, model)
    try:
        complexity_words = complexity_text.split()
        for word in reversed(complexity_words):
            if word.isdigit():
                return int(word)
        return 20
    except ValueError:
        return 20

class SummarizingChatBot:
    """
    A chatbot that uses AI to generate responses, summarize conversation history,
    and assess conversation complexity dynamically.
    """
    def __init__(self, openai_model="gpt-3.5-turbo", base_history_length=10):
        """
        Initializes a new instance of SummarizingChatBot.
        
        :param openai_model: The model identifier for OpenAI API calls.
        :param base_history_length: The base number of exchanges before considering summarization.
        """
        self.openai_model = openai_model
        self.chat_history = []  # List to store the conversation history.
        self.base_history_length = base_history_length  # Base number of exchanges for summarization trigger.

    def get_response(self, input_text):
        """
        Processes the user input, generates a response, and updates the conversation history.
        
        :param input_text: The user's input to which the bot should respond.
        :return: The generated response from the bot.
        """
        chat_history_str = "\n".join(self.chat_history)
        prompt = f"{chat_history_str}\nUser: {input_text}\nBot:"
        response = generate_response(prompt, self.openai_model)
        self.update_history(input_text, response)
        return response

    def update_history(self, user_input, bot_response):
        """
        Updates the conversation history with the latest exchange and manages its length.
        
        :param user_input: The user's latest input.
        :param bot_response: The bot's response to the user's input.
        """
        self.chat_history.extend([f"User: {user_input}", f"Bot: {bot_response}"])
        complexity_score = assess_complexity(self.chat_history, self.openai_model)
        adaptive_history_length = max(self.base_history_length, min(50, complexity_score // 5))
        if len(self.chat_history) > adaptive_history_length * 2:
            summarized_history = summarize_text(" ".join(self.chat_history), self.openai_model)
            self.chat_history = [summarized_history] + self.chat_history[-(adaptive_history_length // 2):]