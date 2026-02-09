import streamlit as st

# Define a function that generates a response based on user input
def echo_agent(user_text: str) -> str:
    return f"You said: {user_text}"

def append_history(role: str, content: str) -> None:
    st.session_state.history.append({"role": role, "content": content})

# Configure the Streamlit page with a title
st.set_page_config(page_title="Echo Agent")

# Display the main title of the web application
st.title("Echo Agent")

# Add a button to clear the chat history
if st.button("Clear History"):
    st.session_state.history = []

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Create an input box for the user to type a message
user_text = st.chat_input("Type a message...")

# Check if the user has entered any text
if user_text:
    # Add the user's message to the chat history
    append_history("user", user_text)

    # Generate a reply using the echo_agent function
    reply = echo_agent(user_text)
    append_history("assistant", reply)

# Display the chat history in the main interface
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])