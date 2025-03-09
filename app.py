import gradio as gr
from huggingface_hub import InferenceClient
import random
import os

# Initialize with OPT-350M, token from environment variable
client = InferenceClient(
    model="facebook/opt-350m",
    token=os.getenv("HF_TOKEN")  # Fetch token from secrets
)

# Resource bank
COPING_STRATEGIES = [
    "Try the 4-7-8 breathing technique: inhale for 4 seconds, hold for 7, exhale for 8—repeat three times.",
    "Write down three things you’re grateful for today; it shifts your focus gently.",
    "Step outside for a minute—fresh air can reset your mind."
]

# Enhanced prompt
SYSTEM_PROMPT = (
    "You are MindSpace Companion, an empathetic, professional mental health aide designed to provide detailed, supportive, and engaging responses (100-200 words). "
    "Use a warm, conversational tone, starting every reply with 'Hello, I’m here for you.' "
    "Structure responses: 1) Acknowledge the user’s feelings with empathy, 2) Offer two practical coping strategies or mindfulness tips, 3) Ask an open-ended question to keep the conversation flowing. "
    "Avoid medical advice; focus on emotional support. "
    "Example: User: 'I’m anxious.' Response: 'Hello, I’m here for you. Anxiety can feel like a storm brewing inside, can’t it? I’m here to weather it with you. First, try grounding yourself—name three things you can see, touch, and hear right now; it pulls you back to the present. Second, take five slow breaths, imagining the tension melting away with each exhale. What’s sparking your anxiety today—want to unpack it together?'"
)

def chatbot(message, history):
    try:
        # Build context from history
        context = "\n".join([f"User: {h[0]}\nAssistant: {h[1]}" for h in history]) if history else ""
        # Extract keyword for personalization
        keywords = [word for word in message.lower().split() if word in ["work", "overwhelmed", "anxious", "sad"]]
        keyword = keywords[0] if keywords else "this"
        
        prompt = f"{SYSTEM_PROMPT}\n{context}\nUser: {message}\nAssistant: Hello, I’m here for you. I sense {keyword} is weighing on you—"
        response = client.text_generation(
            prompt,
            max_new_tokens=300,
            temperature=0.85,
            top_p=0.9,
            stop=["User:", "Assistant:"]
        )
        # Add coping strategy
        strategy = random.choice(COPING_STRATEGIES)
        formatted_response = (
            f"{response.strip()}\n\n"
            f"**Here’s a quick tip:** {strategy} How does that feel for you?"
        )
        
        with open("chat_log.txt", "a", encoding="utf-8") as f:
            f.write(f"User: {message}\nAssistant: {formatted_response}\n\n")
        
        return formatted_response
    except Exception as e:
        error_msg = f"Hello, I’m here for you. I hit a snag—let’s try again! (Error: {str(e)})"
        with open("chat_log.txt", "a", encoding="utf-8") as f:
            f.write(f"User: {message}\nAssistant: {error_msg}\n\n")
        return error_msg

# Gradio interface with custom Neobrutalist CSS
interface = gr.ChatInterface(
    fn=chatbot,
    title="MindSpace Companion",
    description="A supportive chatbot for mental well-being, powered by OPT-350M.",
    theme="soft",
    examples=["I’m feeling overwhelmed today.", "Can you suggest a breathing exercise?", "I need help calming down."],
    submit_btn="Send",
    css="""
    .chatbox { border: 4px solid #000; box-shadow: 5px 5px 0 #FF6B6B; background-color: #F5F5F5; }
    .message { font-family: 'Courier New', monospace; color: #000; }
    .gradio-container { max-height: 80vh; overflow: hidden; }
    """
)

interface.launch()