# -*- coding: utf-8 -*-
"""
Streamlit App for MCQ Generator with PDF Support
"""

import os
import json
import traceback
import pandas as pd
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the MCQGenerator - adjust the import based on your actual structure
try:
    # Try importing as functions
    from src.mcqgenerator import generate_evaluate_chain, get_table_data
    USE_FUNCTIONS = True
    MCQGenerator = None
except (ImportError, AttributeError):
    try:
        # Try importing the class from a submodule
        from src.mcqgenerator.MCQGenerator import MCQGenerator as MCQGen
        MCQGenerator = MCQGen
        USE_FUNCTIONS = False
    except (ImportError, AttributeError):
        try:
            # Try importing from __init__.py
            import src.mcqgenerator as mcq_module
            # Check if it's a class or module
            if hasattr(mcq_module, 'MCQGenerator'):
                MCQGenerator = mcq_module.MCQGenerator
                USE_FUNCTIONS = False
            elif hasattr(mcq_module, 'generate_evaluate_chain'):
                generate_evaluate_chain = mcq_module.generate_evaluate_chain
                get_table_data = mcq_module.get_table_data
                USE_FUNCTIONS = True
                MCQGenerator = None
            else:
                st.error("❌ Could not find MCQGenerator class or functions in src.mcqgenerator")
                st.info("Please check your src/mcqgenerator/__init__.py file")
                st.stop()
        except ImportError as e:
            st.error(f"❌ Import error: {e}")
            st.info("Please check your src/mcqgenerator structure")
            st.stop()

# Page configuration
st.set_page_config(
    page_title="MCQ Generator",
    page_icon="📝",
    layout="wide"
)

# Title
st.title("📝 MCQ Generator")
st.markdown("Generate Multiple Choice Questions from your text using AI")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input - load from .env first
    default_api_key = os.getenv("GROQ_API_KEY", "")
    
    if default_api_key:
        st.success("✅ API Key loaded from .env file")
        api_key = default_api_key
        # Show masked key
        masked_key = default_api_key[:4] + "*" * (len(default_api_key) - 8) + default_api_key[-4:] if len(default_api_key) > 8 else "****"
        st.text_input(
            "Groq API Key",
            value=masked_key,
            disabled=True,
            help="API Key loaded from .env file"
        )
    else:
        st.warning("⚠️ No API Key found in .env file")
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            value="",
            help="Enter your Groq API key or add it to .env file as GROQ_API_KEY=your_key"
        )
    
    # Number of MCQs
    mcq_count = st.number_input(
        "Number of MCQs",
        min_value=1,
        max_value=20,
        value=3,
        help="Number of questions to generate"
    )
    
    # Subject
    subject = st.text_input(
        "Subject",
        value="Machine Learning",
        help="Subject/topic of the questions"
    )
    
    # Difficulty level
    tone = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1
    )

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

# Main content area
uploaded_file = st.file_uploader(
    "📄 Upload a file",
    type=["txt", "pdf"],
    help="Upload a TXT or PDF file to generate MCQs from"
)

# Text input as alternative
text_input = st.text_area(
    "Or paste your text here:",
    height=200,
    placeholder="Enter the text you want to generate MCQs from..."
)

# Load response template
@st.cache_data
def load_response_template():
    """Load or create response template"""
    # Default template
    default_template = {
        "1": {
            "mcq": "sample question",
            "options": {
                "a": "option 1",
                "b": "option 2",
                "c": "option 3",
                "d": "option 4"
            },
            "correct": "a"
        }
    }
    
    try:
        # Try multiple encodings
        for encoding in ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1']:
            try:
                with open("Response.json", "r", encoding=encoding) as f:
                    content = f.read()
                    if content.strip():
                        template = json.loads(content)
                        # Re-save with proper UTF-8 encoding
                        with open("Response.json", "w", encoding="utf-8") as fw:
                            json.dump(template, fw, indent=4)
                        return template
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
    except FileNotFoundError:
        pass
    
    # If all fails, create new file with default template
    try:
        with open("Response.json", "w", encoding="utf-8") as f:
            json.dump(default_template, f, indent=4)
    except:
        pass
    
    return default_template

# Generate button
if st.button("🚀 Generate MCQs", type="primary", use_container_width=True):
    
    # Validation
    if not api_key:
        st.error("❌ Please enter your Groq API Key or add it to your .env file")
        st.info("💡 To use .env file: Create a file named '.env' in your project folder and add: GROQ_API_KEY=your_api_key_here")
        st.stop()
    
    # Get text from file or input
    text = ""
    if uploaded_file:
        try:
            file_type = uploaded_file.name.split(".")[-1].lower()
            
            if file_type == "pdf":
                st.info("📄 Processing PDF file...")
                text = extract_text_from_pdf(uploaded_file)
            elif file_type == "txt":
                st.info("📄 Processing TXT file...")
                text = uploaded_file.read().decode("utf-8")
            else:
                st.error("❌ Unsupported file type")
                st.stop()
                
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.stop()
    elif text_input:
        text = text_input
    else:
        st.error("❌ Please upload a file or enter text")
        st.stop()
    
    if not text.strip():
        st.error("❌ The provided text is empty or could not be extracted")
        st.stop()
    
    # Show text info
    word_count = len(text.split())
    st.info(f"📊 Processing {len(text)} characters ({word_count} words) of text...")
    
    # Show preview of extracted text
    with st.expander("👁️ Preview extracted text"):
        st.text(text[:500] + "..." if len(text) > 500 else text)
    
    # Generate MCQs
    with st.spinner("🔄 Generating MCQs... This may take a few moments..."):
        try:
            # Load template
            response_template = load_response_template()
            
            # Generate based on import type
            if USE_FUNCTIONS:
                # If using functions directly
                response = generate_evaluate_chain(
                    text=text,
                    number=mcq_count,
                    subject=subject,
                    tone=tone,
                    response_json=json.dumps(response_template),
                    api_key=api_key
                )
                quiz_data_func = get_table_data
            else:
                # If using class
                try:
                    generator = MCQGenerator(api_key)
                    response = generator.generate_evaluate_chain(
                        text=text,
                        number=mcq_count,
                        subject=subject,
                        tone=tone,
                        response_json=json.dumps(response_template)
                    )
                    quiz_data_func = generator.get_table_data
                except TypeError as e:
                    st.error(f"❌ Error initializing MCQGenerator: {e}")
                    st.info("💡 Check if MCQGenerator is a class or if it needs different parameters")
                    raise
            
            # Check if response is valid
            if not response:
                st.error("❌ Failed to generate MCQs. Please try again.")
                st.stop()
            
            # Display Quiz
            quiz_content = response.get("quiz", "")
            if quiz_content:
                st.success("✅ MCQs generated successfully!")
                
                # Parse and display as table
                try:
                    quiz_data = quiz_data_func(quiz_content)
                    
                    if quiz_data:
                        st.header("📋 Generated Questions")
                        
                        # Convert to DataFrame for better display
                        df_data = []
                        for key, value in quiz_data.items():
                            options_str = "\n".join([f"{k}) {v}" for k, v in value.get('options', {}).items()])
                            df_data.append({
                                "Question": value.get('mcq', 'N/A'),
                                "Options": options_str,
                                "Correct Answer": value.get('correct', 'N/A')
                            })
                        
                        df = pd.DataFrame(df_data)
                        df.index = df.index + 1
                        df.index.name = "No."
                        
                        st.dataframe(df, use_container_width=True)
                        
                        # Display individual questions
                        st.header("📝 Detailed View")
                        for i, (key, value) in enumerate(quiz_data.items(), 1):
                            with st.expander(f"Question {i}: {value.get('mcq', 'N/A')[:50]}..."):
                                st.markdown(f"**Q{i}: {value.get('mcq', 'N/A')}**")
                                st.markdown("**Options:**")
                                for opt_key, opt_val in value.get('options', {}).items():
                                    st.markdown(f"- {opt_key}) {opt_val}")
                                st.markdown(f"**✅ Correct Answer: {value.get('correct', 'N/A')}**")
                    else:
                        st.warning("⚠️ Could not parse quiz into structured format")
                        st.markdown("### Raw Quiz Output:")
                        st.text(quiz_content)
                        
                except Exception as e:
                    st.warning(f"⚠️ Could not parse quiz data: {e}")
                    st.markdown("### Raw Quiz Output:")
                    st.text(quiz_content)
                
                # Display Review
                review_content = response.get("review", "")
                if review_content:
                    st.header("📊 Complexity Analysis")
                    st.info(review_content)
                
                # Download option
                st.header("💾 Download")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Download Quiz (TXT)",
                        data=quiz_content,
                        file_name=f"mcq_quiz_{subject.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    if 'df' in locals():
                        csv = df.to_csv(index=True)
                        st.download_button(
                            label="📥 Download Quiz (CSV)",
                            data=csv,
                            file_name=f"mcq_quiz_{subject.replace(' ', '_')}.csv",
                            mime="text/csv"
                        )
            else:
                st.error("❌ No quiz content generated")
                
        except Exception as e:
            st.error(f"❌ Error generating MCQs: {str(e)}")
            with st.expander("🔍 Show detailed error"):
                st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Built with Streamlit | Powered by Groq AI</p>
    </div>
    """,
    unsafe_allow_html=True
)