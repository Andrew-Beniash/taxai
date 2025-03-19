"""
Streamlit application for the AI-powered tax law system.

This is a simple UI that allows users to interact with the tax law AI API endpoint.
"""

import streamlit as st
import requests
import json
import time

# Define the API endpoint
API_URL = "http://localhost:8000/api/v1/query"
HEALTH_URL = "http://localhost:8000/health"

# Configure the page
st.set_page_config(
    page_title="Tax Law AI Assistant",
    page_icon="💰",
    layout="wide"
)

# Add a title and description
st.title("🤖 Tax Law AI Assistant")
st.markdown("""
This AI assistant provides accurate information about tax laws, regulations, and IRS policies.
Ask any tax-related question and get precise, factual information with relevant citations.
""")

# Add a sidebar with system status
st.sidebar.title("System Status")

# Check API status
try:
    health_response = requests.get(HEALTH_URL)
    if health_response.status_code == 200:
        health_data = health_response.json()
        if health_data.get("model_loaded"):
            st.sidebar.success("✅ API is online and model is loaded")
        else:
            st.sidebar.warning("⚠️ API is online but model is still loading")
    else:
        st.sidebar.error("❌ API is offline")
except:
    st.sidebar.error("❌ API is offline")

# Add sample questions
st.sidebar.title("Sample Questions")
sample_questions = [
    "What are the deductions available for small businesses?",
    "How can I qualify for a home office deduction?",
    "What are the tax implications of business travel expenses?",
    "Are meals tax deductible for business purposes?",
    "What is Section 179 deduction and how does it work?"
]

for question in sample_questions:
    if st.sidebar.button(question):
        st.session_state.query = question

# Create a text input for the query
if "query" not in st.session_state:
    st.session_state.query = ""

query = st.text_area("Ask a tax-related question:", height=100, value=st.session_state.query)

# Create a button to submit the query
col1, col2 = st.columns([1, 5])
with col1:
    submit_button = st.button("Submit", type="primary")

# Create a placeholder for the response
response_placeholder = st.empty()

# Display the conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Process the query when the button is clicked
if submit_button and query:
    # Show a loading spinner
    with st.spinner("Generating response..."):
        # Create the API request
        headers = {"Content-Type": "application/json"}
        data = {"query": query}
        
        try:
            # Send the request
            start_time = time.time()
            response = requests.post(API_URL, headers=headers, data=json.dumps(data))
            end_time = time.time()
            
            # Check if the request was successful
            if response.status_code == 200:
                # Extract the response data
                result = response.json()
                
                # Add to conversation history
                st.session_state.conversation.append({
                    "query": query,
                    "response": result["response"],
                    "citations": result["citations"],
                    "confidence_score": result["confidence_score"],
                    "processing_time": result["processing_time"]
                })
                
                # Clear the query input
                st.session_state.query = ""
                
            else:
                st.error(f"Error: {response.status_code}")
                st.error(response.text)
                
        except Exception as e:
            st.error(f"Request failed: {str(e)}")
    
# Display the conversation history in reverse order (most recent first)
for i, item in enumerate(reversed(st.session_state.conversation)):
    with st.container():
        st.markdown("---")
        st.markdown(f"**Question:**")
        st.markdown(f"{item['query']}")
        
        st.markdown(f"**Answer:**")
        st.markdown(f"{item['response']}")
        
        if item['citations']:
            st.markdown(f"**Citations:**")
            for citation in item['citations']:
                st.markdown(f"- {citation}")
        
        st.markdown(f"**Confidence Score:** {item['confidence_score']:.2f}")
        st.markdown(f"**Processing Time:** {item['processing_time']:.2f} seconds")

# Add a button to clear the conversation history
if st.session_state.conversation:
    if st.sidebar.button("Clear Conversation"):
        st.session_state.conversation = []
        st.experimental_rerun()
