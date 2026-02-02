import streamlit as st
import random

# Configure the Streamlit page with a title
st.set_page_config(page_title="Rule-based Agent")

# Display the main title of the web application
st.title("Rule-based Agent")

# Define a function that generates responses based on predefined rules
def rule_based_agent(user_text: str) -> str:
    text = user_text.lower().strip()

    # Respond to greetings
    greetings = ["Hello! Tell me what you're feeling today.", 
                 "Hi there! What's on your mind?", 
                 "Hey! How are you feeling today?"]
    if text in {"hi", "hello", "hey"}:
        return random.choice(greetings)
    # Respond to statements about feelings
    if text.startswith("i feel "):
        return "Thanks for sharing. What do you think is causing that feeling?"
    # Respond to mentions of deadlines
    if "deadline" in text:
        return "What's the deadline date, and what are the next two tasks you can do?"
    # Default response for unrecognized input
    return None


# Initialize the session state to store conversation messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Hi! I am a test chatbot."}
    ]

# Display all previous messages in the chat interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Create an input box for the user to type a message
user_text = st.chat_input("Type a message...")

# Check if the user has entered any text
if user_text:
    # Add the user's message to the session state
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
    # Generate a reply using the rule-based agent function
    reply = rule_based_agent(user_text)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)