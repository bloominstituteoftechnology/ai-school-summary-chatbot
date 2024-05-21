import os
from dotenv import load_dotenv
import openai

load_dotenv()
# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_response(prompt, model="gpt-3.5-turbo"):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].text.strip()

def summarize_text(text, model="gpt-3.5-turbo"):
    summary_prompt = f"Summarize this conversation:\n{text}"
    return generate_response(summary_prompt, model)

def assess_complexity(history, model="gpt-3.5-turbo"):
    # Join the conversation history into a single string.
    conversation = ' '.join(history)

    # Define a detailed prompt that explains what complexity means in this context.
    complexity_prompt = (
        "Please assess the complexity of the following conversation based on the diversity of topics, "
        "the depth of the discussion, and the linguistic variety. A higher score should indicate more "
        "complex discussions involving multiple topics, nuanced discussions, and a richer vocabulary. "
        "Score the conversation from 1 (very simple) to 100 (very complex):\n\n"
        f"{conversation}\n\n"
        "Complexity Score:"
    )

    # Generate a response from OpenAI using the defined prompt.
    complexity_text = generate_response(complexity_prompt, model)

    try:
        # Try to extract and return the complexity score as an integer.
        return int(complexity_text.split()[-1])
    except ValueError:
        # Return a default moderate complexity score if parsing fails.
        return 20

class SummarizingChatBot:
    def __init__(self, openai_model="gpt-3.5-turbo", base_history_length=10):
        """
        Initializes a new instance of the SummarizingChatBot.
        
        :param openai_model: The model identifier for the OpenAI API to use for generating responses.
        :param base_history_length: The base number of message exchanges to keep before considering summarization.
        """
        self.openai_model = openai_model  # Model to use for OpenAI requests.
        self.chat_history = []  # List to store the history of the conversation.
        self.base_history_length = base_history_length  # Minimum number of exchanges before summarization.

    def get_response(self, input_text):
        """
        Generates a response from the chatbot based on the user's input text.

        :param input_text: The input text from the user.
        :return: The generated response from the chatbot.
        """
        # Create a prompt string using the current chat history and the new user input.
        chat_history_str = "\n".join(self.chat_history)
        prompt = f"{chat_history_str}\nUser: {input_text}\nBot:"

        # Use the OpenAI API to generate a response based on the prompt.
        response = generate_response(prompt, self.openai_model)

        # Update the conversation history with the new exchange.
        self.update_history(input_text, response)

        return response

    def update_history(self, user_input, bot_response):
        """
        Updates the chat history and manages the history length by summarizing if necessary.

        :param user_input: The latest user input to add to the history.
        :param bot_response: The latest bot response to add to the history.
        """
        # Append the new user input and bot response to the history.
        self.chat_history.extend([f"User: {user_input}", f"Bot: {bot_response}"])

        # Assess the complexity of the current conversation history.
        complexity_score = assess_complexity(self.chat_history, self.openai_model)

        # Calculate the adaptive history length based on the complexity score.
        adaptive_history_length = max(self.base_history_length, min(50, complexity_score // 5))

        # Summarize the conversation history if it exceeds twice the adaptive history length.
        if len(self.chat_history) > adaptive_history_length * 2:
            summarized_history = summarize_text(" ".join(self.chat_history), self.openai_model)
            # Reset the history to include the summary and the most recent exchanges.
            self.chat_history = [summarized_history] + self.chat_history[-(adaptive_history_length // 2):]
