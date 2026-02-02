import streamlit as st

# Configure the Streamlit page with a title and an icon
st.set_page_config(page_title="Echo Agent")

# Display the main title of the web application with an icon
st.title("Echo Agent")

# Create an input box for the user to type a message
user_text = st.chat_input("Type a message...")

# Check if the user has entered any text
if user_text:
    # Display the user's message in the chat interface
    with st.chat_message("user"):
        st.markdown(user_text)
