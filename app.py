import streamlit as st
import os
from google import genai
from google.genai import types
from datetime import datetime
import time
from database import (
    init_database, create_study_session, save_chat_exchange, 
    get_study_sessions, get_chat_history, update_exchange_rating,
    delete_study_session, get_session_stats
)
from subject_categorizer import categorize_question, get_subject_specific_prompt
import io
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide"
)

# Initialize database
try:
    init_database()
except Exception as e:
    st.error(f"Database initialization failed: {e}")
    st.stop()

# Initialize Gemini client
@st.cache_resource
def get_gemini_client():
    """Initialize and return Gemini client with API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY environment variable not found. Please set your Gemini API key.")
        st.stop()
    return genai.Client(api_key=api_key)

def get_enhanced_ai_response(client, question, conversation_history=None, subject_category=None):
    """Get enhanced response from Gemini API with better context and subject-specific prompting"""
    try:
        # Create a system prompt for educational assistance
        system_prompt = """You are a helpful AI study assistant. Your role is to:
        - Provide clear, accurate, and educational responses
        - Break down complex topics into understandable explanations
        - Offer examples when helpful
        - Encourage learning and critical thinking
        - Be patient and supportive
        
        Please provide helpful and educational responses to student questions."""
        
        # Add subject-specific guidance if category is detected
        if subject_category:
            subject_guidance = get_subject_specific_prompt(subject_category)
            if subject_guidance:
                system_prompt += f"\n\nSubject-specific guidance for {subject_category}: {subject_guidance}"
        
        # Build conversation context for Gemini
        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            conversation_context = "Previous conversation context:\n"
            for item in conversation_history:
                conversation_context += f"Student: {item['question']}\nAssistant: {item['answer']}\n\n"
        
        # Combine system prompt, context, and current question
        full_prompt = system_prompt
        if conversation_context:
            full_prompt += f"\n\n{conversation_context}"
        full_prompt += f"\n\nStudent: {question}\nAssistant:"
        
        # Make API call to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000,
            )
        )
        
        return response.text if response.text else "I'm sorry, I couldn't generate a response. Please try again."
        
    except Exception as e:
        return f"Error getting response from AI: {str(e)}"

def export_session_notes(session_data):
    """Export session data as formatted text"""
    output = io.StringIO()
    
    output.write(f"Study Session: {session_data['name']}\n")
    output.write(f"Created: {session_data['created_at']}\n")
    output.write("=" * 50 + "\n\n")
    
    for i, exchange in enumerate(session_data['history'], 1):
        output.write(f"Question {i}:\n{exchange['question']}\n\n")
        output.write(f"Answer {i}:\n{exchange['answer']}\n\n")
        
        if exchange.get('subject_category'):
            output.write(f"Subject: {exchange['subject_category']}\n")
        
        if exchange.get('rating'):
            rating_text = "👍" if exchange['rating'] > 0 else "👎"
            output.write(f"Rating: {rating_text}\n")
        
        if exchange.get('feedback'):
            output.write(f"Feedback: {exchange['feedback']}\n")
        
        output.write(f"Time: {exchange['timestamp']}\n")
        output.write("-" * 30 + "\n\n")
    
    return output.getvalue()

def main():
    # Initialize session state
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    if 'gemini_client' not in st.session_state:
        st.session_state.gemini_client = get_gemini_client()
    
    # Sidebar for session management
    with st.sidebar:
        st.header("📚 Study Sessions")
        
        # Create new session
        if st.button("➕ New Study Session", use_container_width=True):
            session_name = f"Study Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            new_session_id = create_study_session(session_name)
            st.session_state.current_session_id = new_session_id
            st.rerun()
        
        # Load existing sessions
        sessions = get_study_sessions()
        if sessions:
            st.subheader("Recent Sessions")
            for session in sessions[:10]:  # Show last 10 sessions
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(
                        f"{session['name'][:25]}...", 
                        key=f"load_{session['id']}",
                        help=f"Created: {session['created_at']}"
                    ):
                        st.session_state.current_session_id = session['id']
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{session['id']}", help="Delete session"):
                        delete_study_session(session['id'])
                        if st.session_state.current_session_id == session['id']:
                            st.session_state.current_session_id = None
                        st.rerun()
        
        # Session stats
        stats = get_session_stats()
        if stats['total_sessions'] > 0:
            st.subheader("📊 Statistics")
            st.metric("Total Sessions", stats['total_sessions'])
            st.metric("Total Questions", stats['total_exchanges'])
            if stats['average_rating']:
                st.metric("Avg Rating", f"{stats['average_rating']}/5")
    
    # Main content area
    st.title("🎓 AI Study Assistant")
    st.markdown("**Ask any question and get instant AI-powered answers to help with your studies!**")
    
    # Current session indicator
    if st.session_state.current_session_id:
        sessions = get_study_sessions()
        current_session = next((s for s in sessions if s['id'] == st.session_state.current_session_id), None)
        if current_session:
            st.info(f"📝 Current Session: {current_session['name']}")
        else:
            st.warning("⚠️ Current session not found. Please create a new session.")
            st.session_state.current_session_id = None
    else:
        st.warning("💡 Create or select a study session from the sidebar to get started!")
    
    # Question input form
    if st.session_state.current_session_id:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Ask Your Question")
            
            with st.form("question_form", clear_on_submit=True):
                question = st.text_area(
                    "Enter your question here:",
                    height=100,
                    placeholder="e.g., Can you explain photosynthesis? What is the quadratic formula? How does gravity work?"
                )
                
                submitted = st.form_submit_button("Get Answer", use_container_width=True)
                
                if submitted and question.strip():
                    # Show loading spinner
                    with st.spinner("Getting your answer..."):
                        # Categorize the question
                        subject_category = categorize_question(question)
                        
                        # Get conversation history for context
                        conversation_history = get_chat_history(st.session_state.current_session_id)
                        
                        # Get AI response with enhanced context
                        answer = get_enhanced_ai_response(
                            st.session_state.gemini_client, 
                            question, 
                            conversation_history,
                            subject_category
                        )
                        
                        # Save to database
                        save_chat_exchange(
                            st.session_state.current_session_id,
                            question,
                            answer,
                            subject_category
                        )
                        
                        st.rerun()
                
                elif submitted and not question.strip():
                    st.warning("Please enter a question before submitting.")
        
        with col2:
            st.subheader("Quick Tips")
            st.markdown("""
            **How to get better answers:**
            - Be specific in your questions
            - Provide context when needed
            - Ask follow-up questions
            - Break complex topics into parts
            
            **Example questions:**
            - "Explain the water cycle"
            - "What is the Pythagorean theorem?"
            - "How do I solve quadratic equations?"
            - "What causes climate change?"
            """)
        
        # Display chat history for current session
        history = get_chat_history(st.session_state.current_session_id)
        if history:
            st.subheader("📚 Chat History")
            
            # Export session button
            current_sessions = get_study_sessions()
            current_session = next((s for s in current_sessions if s['id'] == st.session_state.current_session_id), None)
            if current_session:
                session_data = {
                    'name': current_session['name'],
                    'created_at': current_session['created_at'],
                    'history': history
                }
                export_text = export_session_notes(session_data)
                st.download_button(
                    label="📄 Export Session Notes",
                    data=export_text,
                    file_name=f"study_session_{current_session['name'].replace(' ', '_')}.txt",
                    mime="text/plain"
                )
            
            # Display each exchange
            for i, exchange in enumerate(reversed(history)):
                with st.expander(
                    f"Q: {exchange['question'][:60]}..." if len(exchange['question']) > 60 
                    else f"Q: {exchange['question']}", 
                    expanded=(i == 0)
                ):
                    # Question and answer
                    st.markdown(f"**Asked:** {exchange['timestamp']}")
                    if exchange.get('subject_category'):
                        st.markdown(f"**Subject:** {exchange['subject_category']}")
                    st.markdown(f"**Question:** {exchange['question']}")
                    st.markdown(f"**Answer:** {exchange['answer']}")
                    
                    # Rating system
                    col1, col2, col3 = st.columns([1, 1, 3])
                    
                    current_rating = exchange.get('rating')
                    
                    with col1:
                        if st.button("👍", key=f"up_{exchange['id']}", 
                                   help="Rate this answer positively"):
                            update_exchange_rating(exchange['id'], 1)
                            st.rerun()
                    
                    with col2:
                        if st.button("👎", key=f"down_{exchange['id']}", 
                                   help="Rate this answer negatively"):
                            update_exchange_rating(exchange['id'], -1)
                            st.rerun()
                    
                    with col3:
                        if current_rating == 1:
                            st.success("👍 Rated positively")
                        elif current_rating == -1:
                            st.error("👎 Rated negatively")
                    
                    # Feedback input
                    feedback_key = f"feedback_{exchange['id']}"
                    feedback = st.text_input(
                        "Additional feedback (optional):",
                        value=exchange.get('feedback', ''),
                        key=feedback_key,
                        placeholder="Share your thoughts on this answer..."
                    )
                    
                    if feedback != exchange.get('feedback', ''):
                        current_rating = exchange.get('rating', 0)
                        update_exchange_rating(exchange['id'], current_rating, feedback)
                    
                    st.divider()
        
        else:
            st.info("💡 Start by asking your first question above! Your chat history will appear here.")
    
    # Footer with usage information
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
        AI Study Assistant - Enhanced with Session Management, Subject Detection & Export | Powered by Gemini API 🌟
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()