import streamlit as st
import base64
from PIL import Image
import io
from typing import Dict
import time

from graph import create_conversation_workflow, AgentState

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_state' not in st.session_state:
        st.session_state.current_state = None
    if 'workflow' not in st.session_state:
        st.session_state.workflow = create_conversation_workflow()
    if 'identified_figure' not in st.session_state:
        st.session_state.identified_figure = None
    if 'processing_message' not in st.session_state:
        st.session_state.processing_message = False

def image_to_base64(image_file) -> str:
    """Convert uploaded image to base64"""
    if image_file is not None:
        bytes_data = image_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode()
        return base64_str
    return None

def initialize_chat_with_image(image_base64: str):
    """Initialize the chat with an image"""
    initial_state = AgentState(
        image_string=image_base64,
        query="who is in this image",
        figure="",
        critique="",
        content=[],
        answer="",
        confirm="",
        revision_number=0,
        max_revisions=3,
        memory={"messages": []}
    )
    
    with st.spinner('Identifying personality...'):
        current_state = st.session_state.workflow.invoke(initial_state)
        st.session_state.current_state = current_state
        st.session_state.identified_figure = current_state['figure']
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"I am now speaking as {current_state['figure']}. How can I help you?"
        })

def process_user_message(user_input: str):
    """Process a user message and get response"""
    if st.session_state.current_state is None:
        return

    # Add user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Set processing flag
    st.session_state.processing_message = True
    
    # Force a rerun to show the user message
    st.rerun()

def handle_pending_response():
    """Handle the pending response if there's one being processed"""
    if st.session_state.processing_message:
        with st.spinner('Thinking...'):
            # Get the last user message
            last_user_message = next(msg["content"] for msg in reversed(st.session_state.messages) 
                                   if msg["role"] == "user")
            
            # Prepare new state
            new_state = {
                **st.session_state.current_state,
                "query": last_user_message,
                "confirm": "",
                "revision_number": 0
            }
            
            # Get response
            current_state = st.session_state.workflow.invoke(new_state)
            st.session_state.current_state = current_state
            
            # Add assistant's response
            st.session_state.messages.append({
                "role": "assistant",
                "content": current_state['answer']
            })
            
            # Reset processing flag
            st.session_state.processing_message = False

def main():
    st.title("Historical Figure Chat")
    
    init_session_state()
    
    with st.sidebar:
        st.header("Upload Image")
        image_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])
        
        if image_file and 'image_processed' not in st.session_state:
            st.image(image_file, caption="Uploaded Image", use_column_width=True)
            image_base64 = image_to_base64(image_file)
            initialize_chat_with_image(image_base64)
            st.session_state.image_processed = True
            st.success(f"Identified as: {st.session_state.identified_figure}")
    
    if st.session_state.identified_figure:
        st.subheader(f"Chat with {st.session_state.identified_figure}")
        
        # Handle any pending response first
        handle_pending_response()
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message..."):
            process_user_message(prompt)
    
    with st.sidebar:
        if st.button("Start New Chat"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

main()