import streamlit as st
import requests
import json
import random
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="⚖️ Electric Power Projects Chatbot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4169E1;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        background-color: #4169E1 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border: 3px solid #000080 !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #4169E1 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border: 3px solid #000080 !important;
        min-height: 300px !important;
    }
    
    .suggestion-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 5px solid #4169E1;
    }
    
    .suggestion-text {
        color: #4169E1 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        cursor: pointer;
    }
    
    .result-container {
        background-color: #4169E1;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 3px solid #000080;
        font-weight: bold;
        font-size: 1.1rem;
        white-space: pre-wrap;
    }
    
    .stButton > button {
        background-color: #4169E1;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        border: 3px solid #000080;
        padding: 0.5rem 2rem;
    }
    
    .stButton > button:hover {
        background-color: #000080;
        color: white;
    }
    
    .target-audience {
        background-color: #e6f3ff;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_KEY = st.secrets.get("EPP2K6", "your-api-key-here")
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# Electric Power Projects Domain Knowledge
DOMAIN_KNOWLEDGE = """
You are an expert chatbot specializing in Electric Power Projects. Your expertise includes:

1. **Balance of Plant (BoP) Services for Thermal Power Projects:**
   - Coal handling and ash handling systems
   - Water treatment plants and cooling water systems
   - BoP electrical systems including switchyards and substations
   - HVAC, firefighting, and compressed air systems
   - Chimney, cooling tower, and structural civil works
   - Fuel oil systems and diesel generator integration
   - Plant piping networks and valve systems
   - Cabling, lighting, and earthing systems
   - Control & instrumentation for auxiliary plants
   - Commissioning and performance testing

2. **Balance of Plant (BoP) Services for Gas Power Projects:**
   - Gas receiving and metering station design
   - Fuel gas conditioning and compression systems
   - Cooling and heat rejection systems
   - Water wash and chemical injection skids
   - Exhaust ducting and flue gas systems
   - Fire protection and gas detection systems
   - Auxiliary power supply and backup systems
   - Noise control enclosures and ventilation
   - Civil works for compressor buildings
   - Integrated control systems

3. **Turnkey Solutions for Solar Power Plants:**
   - Site feasibility and solar resource assessment
   - Complete EPC with PV modules, inverters, mounting structures
   - String and array design optimization
   - Power evacuation and grid interconnection
   - SCADA and remote monitoring systems
   - Battery energy storage integration
   - Civil works: foundation, fencing, drainage
   - Safety systems: lightning protection, earthing
   - Commissioning and performance guarantee
   - Operation manuals and as-built documents

4. **Ground-mounted Solar Installations:**
   - Fixed-tilt vs. single-axis tracking systems
   - Land preparation, grading, pile driving
   - Medium-voltage AC/DC collection systems
   - Inverter station and transformer installation
   - Module cleaning and maintenance access
   - Vegetation control and erosion management
   - Shadow analysis and row spacing optimization
   - Security fencing and CCTV integration
   - Grid compliance with utility standards
   - Environmental impact mitigation

Provide detailed, professional answers related to electric power projects, EPC services, project management, technical specifications, industry standards, and career guidance in the electric power sector.
"""

# Suggested prompts related to Electric Power Projects
SUGGESTED_PROMPTS = [
    "What are the key components of Balance of Plant services in thermal power projects?",
    "Explain the EPC process for solar power plant installation",
    "What are the differences between fixed-tilt and single-axis tracking solar systems?",
    "Describe the cooling water system requirements for gas turbine power plants",
    "What safety systems are essential for solar power plants?",
    "How to optimize string and array design in solar installations?",
    "What are the commissioning requirements for thermal power plant BoP systems?",
    "Explain grid interconnection standards for renewable energy projects",
    "What career opportunities exist in electric power project management?",
    "Describe the environmental impact mitigation strategies for ground-mounted solar farms"
]

def get_chatbot_response(user_query, conversation_history=None):
    """
    Get response from Qwen chatbot API
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {
            "role": "system",
            "content": DOMAIN_KNOWLEDGE
        }
    ]
    
    if conversation_history:
        messages.extend(conversation_history)
    
    messages.append({
        "role": "user",
        "content": user_query
    })
    
    payload = {
        "model": "qwen-max",
        "input": {
            "messages": messages
        },
        "parameters": {
            "result_format": "message",
            "temperature": 0.7,
            "max_tokens": 2000
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "output" in result and "choices" in result["output"]:
            assistant_message = result["output"]["choices"][0]["message"]["content"]
            return assistant_message
        else:
            return "Error: Unexpected API response format"
    
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def initialize_session_state():
    """Initialize session state variables"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'last_query' not in st.session_state:
        st.session_state.last_query = ""
    if 'last_response' not in st.session_state:
        st.session_state.last_response = ""

def main():
    # Header
    st.markdown('<div class="main-header">⚖️ Electric Power Projects Chatbot</div>', unsafe_allow_html=True)
    
    # Target Audience
    st.markdown("""
        <div class="target-audience">
        <b>Target Audience:</b> Project Managers | Professionals in Electric Power Industry | 
        B.E. Electrical and Electronics Students | Job Seekers in Electric Power Industry
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for GitHub info and settings
    with st.sidebar:
        st.header("📚 Repository Information")
        st.markdown("""
        **GitHub Repository:** EPP  
        **License:** MIT  
        **API Key:** EPP2K6  
        **Created:** 2026
        """)
        
        st.divider()
        
        st.header("ℹ️ About")
        st.markdown("""
        This chatbot specializes in:
        - Thermal Power Projects (BoP Services)
        - Gas Power Projects (BoP Services)
        - Solar Power Plants (Turnkey Solutions)
        - Ground-mounted Solar Installations
        """)
        
        st.divider()
        
        if st.button("🔄 Reset Conversation", use_container_width=True):
            st.session_state.conversation_history = []
            st.session_state.last_query = ""
            st.session_state.last_response = ""
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💬 Enter Your Query")
        
        # User input field
        user_query = st.text_input(
            "Type your question about Electric Power Projects:",
            placeholder="E.g., What are BoP services in thermal power plants?",
            label_visibility="collapsed",
            key="user_query_input"
        )
        
        # Suggested prompts section
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💡 Suggested Questions")
        st.markdown("<div class='suggestion-box'>", unsafe_allow_html=True)
        
        # Display 10 random suggested prompts
        random_prompts = random.sample(SUGGESTED_PROMPTS, min(10, len(SUGGESTED_PROMPTS)))
        
        for i, prompt in enumerate(random_prompts, 1):
            st.markdown(f"""
                <div class='suggestion-text' style='margin: 10px 0;'>
                    {i}. {prompt}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Submit button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit_button = st.button("📤 Submit Prompt", use_container_width=True)
    
    with col2:
        st.subheader("📋 Response")
        
        # Result display area
        if st.session_state.last_response:
            st.markdown(f"""
                <div class='result-container'>
                <b>Query:</b> {st.session_state.last_query}
                
                <br><br>
                <b>Response:</b><br>
                {st.session_state.last_response}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class='result-container' style='min-height: 300px; display: flex; align-items: center; justify-content: center;'>
                <i>Enter your query and click Submit to get a response...</i>
                </div>
            """, unsafe_allow_html=True)
    
    # Handle form submission
    if submit_button and user_query.strip():
        with st.spinner("🔄 Processing your query..."):
            # Get response from chatbot
            response = get_chatbot_response(user_query, st.session_state.conversation_history)
            
            # Update session state
            st.session_state.last_query = user_query
            st.session_state.last_response = response
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                "role": "user",
                "content": user_query
            })
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Rerun to display the response
            st.rerun()
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
        <b>Electric Power Projects Chatbot</b> | Powered by Qwen | 
        GitHub: <a href='https://github.com/amrithtech23-ux/EPP' target='_blank'>EPP Repository</a> | 
        License: MIT
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
