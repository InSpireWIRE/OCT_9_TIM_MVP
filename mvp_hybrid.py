import streamlit as st
import requests
import json
import csv
import io
import time
from datetime import datetime

# Helper function for email formatting - EXACT COPY FROM ORIGINAL
def format_results_for_email(results, search_query, search_type):
    """Format search results for email - reusing your existing report format"""
    email_body = f"T!M TRANSCRIPT SEARCH REPORT\n"
    email_body += f"{'='*50}\n"
    email_body += f"REDUCE THE GRIND. REVEAL THE BRILLIANCE.\n"
    email_body += f"{'='*50}\n\n"
    email_body += f"Search Query: {search_query}\n"
    email_body += f"Search Type: {search_type}\n"
    email_body += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    email_body += f"Total Results: {len(results)}\n\n"
    email_body += f"{'='*50}\n"
    email_body += f"SEARCH RESULTS\n"
    email_body += f"{'='*50}\n"
    
    for i, r in enumerate(results[:20], 1):  # Limit to 20 for email
        email_body += f"\nResult #{i}\n"
        email_body += f"Speaker: {r.get('speaker', 'Unknown')}\n"
        email_body += f"Time: {r.get('time_code', '00:00:00')}\n"
        email_body += f"Source: {r.get('source_file', 'Unknown')}\n"
        if r.get('score'):
            email_body += f"Relevance: {r.get('score'):.1f}/10\n"
        email_body += f"\nQuote:\n{r.get('exact_quote', '')}\n"
        email_body += "-"*50 + "\n"
    
    return email_body

# ENHANCED CSS WITH HTML-INSPIRED DARK THEME
st.markdown("""
<style>
    /* === CORE DARK THEME FROM HTML === */
    .stApp {
        background-color: #0A0A0F;
        background: linear-gradient(135deg, #0A0A0F 0%, #1A1A2E 50%, #0A0A0F 100%);
        color: #F0F0F5;
    }
    
    /* === CUSTOM T!M TITLE WITH CYAN ! === */
    .custom-title {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -0.02em;
        border-bottom: 3px solid #00F5FF;
        padding-bottom: 1rem;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 20px rgba(0, 245, 255, 0.5);
    }
    
    .custom-title .cyan-exclamation {
        color: #00F5FF;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.8);
    }
    
    /* === PANEL STYLING FROM HTML === */
    .panel {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        margin: 1rem 0;
    }
    
    /* === HEADER STYLING === */
    h1 {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -1px;
        border-bottom: 3px solid #00F5FF;
        padding-bottom: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* TAGLINE - LARGER */
    .tagline {
        color: #00F5FF;
        font-size: 3rem !important;
        font-weight: 700;
        letter-spacing: 3px;
        margin: 1rem 0;
        text-transform: uppercase;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    }
    
    /* VERSION - HALF AS LARGE = 2.25rem */
    .version {
        color: #999999;
        font-size: 2.25rem !important;
        font-weight: 700;
        margin-bottom: 2rem;
        line-height: 1.2;
    }
    
    /* === SECTION HEADERS === */
    h2 {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 2rem !important;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #00F5FF 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h3 {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 2rem !important;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }
    
    /* === LABELS === */
    .stTextInput > label,
    .stFileUploader > label,
    .stSelectbox > label {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 1rem;
    }
    
    /* === CHECKBOX LABELS === */
    .stCheckbox > label {
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 2.5rem !important;
    }
    
    /* RADIO LABELS - WHITE */
    .stRadio > label {
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 1rem;
    }
    
    /* RADIO OPTIONS - WHITE WITH DARK BACKGROUND */
    .stRadio > div {
        background-color: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stRadio > div label {
        font-size: 2.5rem !important;
        font-weight: 600;
        color: #FFFFFF !important;
    }
    
    .stRadio [data-baseweb="radio"] > div {
        color: #FFFFFF !important;
    }
    
    div[role="radiogroup"] label {
        color: #FFFFFF !important;
        font-size: 2.5rem !important;
    }
    
    /* === INPUT FIELDS - DARK THEME === */
    .stTextInput > div > div > input {
        background-color: rgba(10, 10, 15, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1rem;
        color: #F0F0F5 !important;
        font-size: 1.33rem !important;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        outline: none;
        border-color: #00F5FF;
        box-shadow: 0 0 0 3px rgba(0, 245, 255, 0.1);
    }
    
    /* === TRANSCRIPT SELECTOR === */
    .transcript-selector {
        background-color: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(0, 245, 255, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .transcript-button {
        background-color: rgba(10, 10, 15, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #00F5FF;
        padding: 0.66rem;
        margin: 0.33rem 0;
        border-radius: 6px;
        font-size: 1.33rem !important;
        font-weight: 600;
        width: 100%;
        text-align: left;
        transition: all 0.3s ease;
    }
    
    .transcript-button:hover {
        background-color: #00F5FF;
        color: #0A0A0F;
        transform: translateX(5px);
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    }
    
    .transcript-selected {
        background-color: #00F5FF !important;
        color: #0A0A0F !important;
        font-weight: 800;
    }
    
    /* EXPANDER STYLING */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 3px solid #00F5FF;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1.67rem !important;
        color: #FFFFFF !important;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(0, 245, 255, 0.05);
        border-color: #00F5FF;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(10, 10, 15, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0 0 6px 6px;
        padding: 1.5rem;
        font-size: 2rem !important;
        line-height: 1.6;
    }
    
    /* === OUTPUT TEXT === */
    .streamlit-expanderContent p {
        font-size: 2rem !important;
        line-height: 1.6;
        margin-bottom: 1rem;
        color: #F0F0F5 !important;
    }
    
    .streamlit-expanderContent strong {
        color: #00F5FF;
        font-size: 2.07rem !important;
    }
    
    /* === BUTTONS WITH HTML STYLING === */
    .stButton > button {
        background: linear-gradient(135deg, #00F5FF 0%, #0EA5E9 100%);
        color: #0A0A0F;
        border: none;
        padding: 1.5rem 2.5rem;
        font-weight: 700;
        font-size: 3.5rem !important;
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0, 245, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 245, 255, 0.4);
    }
    
    .stButton > button:disabled {
        background: rgba(255, 255, 255, 0.1);
        color: #666666;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    /* === FILE UPLOADER === */
    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.02);
        border: 2px dashed rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #00F5FF;
        background: rgba(0, 245, 255, 0.05);
    }

    .stFileUploader label {
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 2rem !important;
    }

    /* Dropzone styling */
    section[data-testid="stFileUploadDropzone"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 8px;
        padding: 2rem;
    }

    /* "Drag and drop" text */
    section[data-testid="stFileUploadDropzone"] small {
        color: #F0F0F5 !important;
        font-size: 1.8rem !important;
        font-weight: 600;
    }

    /* Hide the duplicate upload instructions */
    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }
    
    /* Actually hide the drag and drop text */
    section[data-testid="stFileUploadDropzone"] small {
        display: none !important;
    }

    /* "Browse files" button */
    section[data-testid="stFileUploadDropzone"] button {
        background: linear-gradient(135deg, #00F5FF 0%, #0EA5E9 100%) !important;
        color: #0A0A0F !important;
        border: none !important;
        padding: 1rem 2rem !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        border-radius: 6px;
        box-shadow: 0 4px 15px rgba(0, 245, 255, 0.3);
    }

    section[data-testid="stFileUploadDropzone"] button:hover {
        background: linear-gradient(135deg, #0EA5E9 0%, #00F5FF 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 245, 255, 0.4);
    }
    
    /* File name display */
    section[data-testid="stFileUploadDropzone"] div {
        color: #F0F0F5 !important;
    }
    
    /* === UPLOADED FILE DISPLAY === */
    .stFileUploader [data-testid="stFileUploaderFileName"] {
        color: #F0F0F5 !important;
        font-size: 1.8rem !important;
        font-weight: 600;
        background-color: rgba(0, 245, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }

    /* Delete file X button */
    .stFileUploader [data-testid="stFileUploaderDeleteBtn"] {
        color: #ff5252 !important;
        font-size: 2rem !important;
        font-weight: 700;
    }

    /* === MESSAGES === */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.2), rgba(0, 188, 212, 0.2));
        color: #00FF00 !important;
        border-left: 4px solid #00FF00;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 700;
        font-size: 2.5rem !important;
    }
    
    .stError {
        background-color: rgba(244, 67, 54, 0.1);
        color: #ff5252 !important;
        border-left: 4px solid #f44336;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 600;
        font-size: 2.5rem !important;
    }
    
    .stWarning {
        background-color: rgba(255, 152, 0, 0.1);
        color: #ffab40 !important;
        border-left: 4px solid #ff9800;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 600;
        font-size: 2.5rem !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.1), rgba(0, 180, 216, 0.1));
        color: #00F5FF !important;
        border-left: 4px solid #00F5FF;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 600;
        font-size: 2.5rem !important;
    }
    
    /* === DOWNLOAD BUTTONS === */
    .stDownloadButton > button {
        background-color: rgba(26, 26, 46, 0.8);
        border: 2px solid #00F5FF;
        color: #00F5FF;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 2rem !important;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #00F5FF 0%, #7C3AED 100%);
        color: #0A0A0F;
        border-color: transparent;
    }
    
    /* === CONNECTION STATUS === */
    .connection-status-green {
        background: linear-gradient(135deg, #10B981 0%, #0EA5E9 100%);
        color: #0A0A0F;
        font-weight: 900;
        font-size: 1.5rem !important;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-align: center;
        border: 2px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
    }

    .connection-status-red {
        background: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        font-weight: 900;
        font-size: 1.5rem !important;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-align: center;
        border: 2px solid rgba(239, 68, 68, 0.3);
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
    }
    
    /* === FOOTER === */
    .footer {
        text-align: center;
        color: #999999;
        font-size: 1.5rem !important;
        padding: 2rem 0;
        margin-top: 4rem;
        border-top: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    /* === ALL TEXT WHITE & READABLE === */
    p, div, span, label {
        color: #F0F0F5 !important;
        font-size: 2rem !important;
    }
    
    /* Caption text for disabled button */
    .stCaption {
        color: #999999 !important;
        font-size: 1.8rem !important;
    }
    
    /* === ENTITY RESULTS CARD STYLING === */
    .entity-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    
    .entity-card:hover {
        border-color: rgba(0, 245, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .entity-header {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .entity-list {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .entity-item {
        background: rgba(0, 245, 255, 0.1);
        border: 1px solid rgba(0, 245, 255, 0.3);
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 1.4rem;
        color: #00F5FF;
        font-weight: 600;
    }
    
    /* === DRAMA DETECTION CARD === */
    .drama-card {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.1), rgba(59, 130, 246, 0.1));
        border: 1px solid rgba(124, 58, 237, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    
    .drama-score {
        background: linear-gradient(135deg, #7C3AED 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Page config - PRESERVED FROM ORIGINAL
st.set_page_config(
    page_title="T!M - Transcript !ntelligence Machine", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state - PRESERVED FROM ORIGINAL
if 'selected_transcript_id' not in st.session_state:
    st.session_state.selected_transcript_id = None
if 'selected_transcript_name' not in st.session_state:
    st.session_state.selected_transcript_name = None
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = False

# Header with Cyan ! in T!M - ENHANCED WITH HTML STYLING
st.markdown('<h1 class="custom-title">T<span class="cyan-exclamation">!</span>M - Transcript <span class="cyan-exclamation">!</span>ntelligence Machine</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">REDUCE THE GRIND. REVEAL THE BRILLIANCE.</p>', unsafe_allow_html=True)
st.markdown('<p class="version">MVP Demo Version 1.0</p>', unsafe_allow_html=True)

# Connection section - PRESERVED FROM ORIGINAL
col1, col2 = st.columns([3, 1])
with col1:
    colab_url = st.text_input(
        "Colab API URL",
        placeholder="https://xxxx.ngrok-free.app",
        help="Enter your Colab ngrok URL to connect to the backend"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if colab_url:
        try:
            test = requests.get(f"{colab_url}/test", timeout=3)
            if test.status_code == 200:
                st.markdown('<div class="connection-status-green">CONNECTED</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="connection-status-red">DISCONNECTED</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div class="connection-status-red">DISCONNECTED</div>', unsafe_allow_html=True)

if colab_url:
    # Upload and Search Side-by-Side - PRESERVED FROM ORIGINAL
    st.markdown("---")
    
    upload_col, search_col = st.columns([1, 2])
    
    # UPLOAD SECTION - PRESERVED WITH 360 SECOND TIMEOUT
    with upload_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Upload Transcript")
        uploaded_file = st.file_uploader(
            "",  # Empty label
            type=['docx', 'txt', 'pdf'],
            help="Upload a transcript file to process and make searchable"
        )
        
        if st.button("PROCESS TRANSCRIPT", use_container_width=True, disabled=not uploaded_file):
            if uploaded_file:
                with st.spinner(f"Processing {uploaded_file.name}... (This may take several minutes)"):
                    try:
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        response = requests.post(
                            f"{colab_url}/upload-transcript",
                            files=files,
                            headers={"X-API-Key": "tie_smartco1_demo123"},
                            timeout=360  # 360 SECONDS = 6 MINUTES - PRESERVED
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"{result.get('message', 'Upload successful')}")
                            st.info("Transcript is now searchable!")
                            st.rerun()
                        else:
                            st.error(f"Upload failed: {response.status_code}")
                            try:
                                error_data = response.json()
                                st.error(f"Error: {error_data.get('error', 'Unknown error')}")
                            except:
                                st.error(f"Response: {response.text[:200]}")
                                
                    except requests.exceptions.Timeout:
                        st.error("Upload timed out after 6 minutes - file may be too large or backend is busy")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SEARCH SECTION - PRESERVED FROM ORIGINAL
    with search_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Search Transcripts")
        
        search_type = st.radio(
            "Search Method",
            ["Keyword Search", "Semantic Search (AI)"],
            help="Keyword: Exact matching | Semantic: AI understands meaning"
        )
        
        # Get transcript list - PRESERVED FROM ORIGINAL
        transcripts = []
        transcript_id = None
        
        try:
            transcripts_response = requests.get(
                f"{colab_url}/list-transcripts",
                headers={"X-API-Key": "tie_smartco1_demo123"},
                timeout=10
            )
            
            if transcripts_response.status_code == 200:
                transcripts = transcripts_response.json()
        except:
            transcripts = []
        
        # TRANSCRIPT SELECTOR - PRESERVED FROM ORIGINAL
        if transcripts:
            all_transcripts = st.checkbox("All Transcripts", value=True)
            
            if not all_transcripts:
                st.markdown("### Select Transcript")
                with st.expander(f"📋 Available Transcripts ({len(transcripts)})", expanded=False):
                    for t in transcripts:
                        filename = t['filename']
                        tid = t['id']
                        is_selected = st.session_state.selected_transcript_id == tid
                        
                        button_label = f"{'✅ ' if is_selected else '▫️ '}{filename}"
                        
                        if st.button(button_label, key=f"sel_{tid}", use_container_width=True):
                            st.session_state.selected_transcript_id = tid
                            st.session_state.selected_transcript_name = filename
                            st.rerun()
                
                # DELETE FUNCTIONALITY - PRESERVED FROM ORIGINAL
                if st.session_state.selected_transcript_name:
                    st.success(f"Selected: {st.session_state.selected_transcript_name}")
                    transcript_id = st.session_state.selected_transcript_id
                    
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if not st.session_state.confirm_delete:
                            if st.button("🗑️ Delete", key="delete_transcript", 
                                        help="Delete this transcript permanently"):
                                st.session_state.confirm_delete = True
                                st.rerun()
                        else:
                            st.error("⚠️ Are you SURE? This cannot be undone!")
                            col_yes, col_no = st.columns(2)
                            
                            with col_yes:
                                if st.button("Yes, DELETE", key="confirm_yes"):
                                    if transcript_id:
                                        try:
                                            response = requests.delete(
                                                f"{colab_url}/delete-transcript/{transcript_id}",
                                                headers={
                                                    'X-API-Key': 'tie_smartco1_demo123',
                                                    'Content-Type': 'application/json',
                                                    'ngrok-skip-browser-warning': 'true'
                                                },
                                                timeout=30
                                            )
                                            
                                            if response.status_code == 200:
                                                st.success(f"✅ Deleted: {st.session_state.selected_transcript_name}")
                                                st.session_state.selected_transcript_id = None
                                                st.session_state.selected_transcript_name = None
                                                st.session_state.confirm_delete = False
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error(f"Delete failed: {response.text}")
                                                st.session_state.confirm_delete = False
                                                
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                                            st.session_state.confirm_delete = False
                            
                            with col_no:
                                if st.button("Cancel", key="cancel_delete"):
                                    st.session_state.confirm_delete = False
                                    st.rerun()
        else:
            st.warning("No transcripts found. Upload a transcript first.")
        
        # SEARCH FUNCTIONALITY - PRESERVED FROM ORIGINAL
        search_query = st.text_input(
            "Search Query",
            placeholder="Enter your search terms...",
            help="Try: 'drug task force', 'Tammy', 'Oklahoma'"
        )
        
        if st.button("SEARCH", use_container_width=True):
            if search_query:
                with st.spinner("Searching..."):
                    endpoint = "/api/v2/semantic-search" if search_type == "Semantic Search (AI)" else "/api/v2/keyword-search"
                    
                    try:
                        response = requests.post(
                            f"{colab_url}{endpoint}",
                            json={"query": search_query, "transcript_id": transcript_id},
                            headers={"X-API-Key": "tie_smartco1_demo123"},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            results = response.json()
                            
                            if not results:
                                st.warning(f"No results found for '{search_query}'")
                            else:
                                st.markdown(f"### Results: {len(results)} matches found for '{search_query}'")
                                
                                for i, r in enumerate(results[:10], 1):
                                    speaker = r.get('speaker', 'Unknown')
                                    time_code = r.get('time_code', '00:00:00')
                                    source = r.get('source_file', 'Unknown')
                                    score = r.get('score', 0)
                                    
                                    if search_type == "Semantic Search (AI)" and score > 0:
                                        header = f"{i}. {speaker} [{time_code}] - Relevance: {score:.1f}/10"
                                    else:
                                        header = f"{i}. {speaker} [{time_code}]"
                                    
                                    with st.expander(header):
                                        st.write(f"**Quote:** {r.get('exact_quote', '')}")
                                        st.write(f"**Time:** {time_code}")
                                        st.write(f"**Speaker:** {speaker}")
                                        st.write(f"**Source:** {source}")
                                        if score > 0:
                                            st.write(f"**Relevance Score:** {score:.1f}/10")
                                
                                # DOWNLOAD RESULTS - PRESERVED FROM ORIGINAL
                                if results:
                                    st.markdown("---")
                                    st.subheader("Download Results")
                                    dcol1, dcol2, dcol3 = st.columns(3)
                                    
                                    with dcol1:
                                        # CSV Download - PRESERVED
                                        output = io.StringIO()
                                        writer = csv.writer(output)
                                        writer.writerow(['T!M Search Results'])
                                        writer.writerow(['Query:', search_query])
                                        writer.writerow(['Search Type:', search_type])
                                        writer.writerow(['Time:', datetime.now().strftime('%Y-%m-%d %H:%M')])
                                        writer.writerow([])
                                        writer.writerow(['#', 'Speaker', 'Time', 'Quote', 'Source', 'Relevance'])
                                        
                                        for i, r in enumerate(results, 1):
                                            writer.writerow([
                                                i,
                                                r.get('speaker', ''),
                                                r.get('time_code', ''),
                                                r.get('exact_quote', ''),
                                                r.get('source_file', ''),
                                                f"{r.get('score', 0):.1f}" if r.get('score') else 'N/A'
                                            ])
                                        
                                        st.download_button(
                                            "Download CSV",
                                            data=output.getvalue(),
                                            file_name=f"T!M_results_{search_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                            mime="text/csv",
                                            use_container_width=True
                                        )
                                    
                                    with dcol2:
                                        # Text Report Download - PRESERVED
                                        report = f"T!M TRANSCRIPT SEARCH REPORT\n"
                                        report += f"{'='*50}\n"
                                        report += f"REDUCE THE GRIND. REVEAL THE BRILLIANCE.\n"
                                        report += f"{'='*50}\n\n"
                                        report += f"Search Query: {search_query}\n"
                                        report += f"Search Type: {search_type}\n"
                                        report += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                                        report += f"Total Results: {len(results)}\n\n"
                                        report += f"{'='*50}\n"
                                        report += f"SEARCH RESULTS\n"
                                        report += f"{'='*50}\n"
                                        
                                        for i, r in enumerate(results, 1):
                                            report += f"\nResult #{i}\n"
                                            report += f"Speaker: {r.get('speaker', 'Unknown')}\n"
                                            report += f"Time: {r.get('time_code', '00:00:00')}\n"
                                            report += f"Source: {r.get('source_file', 'Unknown')}\n"
                                            if r.get('score'):
                                                report += f"Relevance: {r.get('score'):.1f}/10\n"
                                            report += f"\nQuote:\n{r.get('exact_quote', '')}\n"
                                            report += "-"*50 + "\n"
                                        
                                        st.download_button(
                                            "Download Report",
                                            data=report,
                                            file_name=f"T!M_report_{search_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                                            mime="text/plain",
                                            use_container_width=True
                                        )
                                    
                                    with dcol3:
                                        # Email Results - PRESERVED FROM ORIGINAL
                                        st.markdown("**Email Results**")
                                        
                                        recipient_email = st.text_input(
                                            "Email to:",
                                            placeholder="example@email.com",
                                            key=f"email_{search_query}_{datetime.now().timestamp()}"
                                        )
                                        
                                        if st.button("📧 Send Email", use_container_width=True, 
                                                    key=f"send_{search_query}_{datetime.now().timestamp()}"):
                                            if recipient_email and "@" in recipient_email:
                                                with st.spinner("Sending email..."):
                                                    try:
                                                        email_body = format_results_for_email(
                                                            results, 
                                                            search_query, 
                                                            search_type
                                                        )
                                                        
                                                        response_email = requests.post(
                                                            f"{colab_url}/send-email",
                                                            headers={"X-API-Key": "tie_smartco1_demo123"},
                                                            json={
                                                                "recipient": recipient_email,
                                                                "subject": f"T!M Results: {search_query}",
                                                                "body": email_body
                                                            },
                                                            timeout=10
                                                        )
                                                        
                                                        if response_email.status_code == 200:
                                                            st.success(f"✅ Email sent to {recipient_email}")
                                                        else:
                                                            st.error(f"Failed to send email: {response_email.text}")
                                                            
                                                    except Exception as e:
                                                        st.error(f"Email error: {str(e)}")
                                            else:
                                                st.warning("Please enter a valid email address")
                                
                        else:
                            st.error(f"Search failed: {response.status_code}")
                            try:
                                error_msg = response.json()
                                st.error(f"Error: {error_msg}")
                            except:
                                st.text(f"Response: {response.text[:500]}")
                                
                    except requests.exceptions.Timeout:
                        st.error("Search timed out - try a simpler query")
                    except Exception as e:
                        st.error(f"Search error: {str(e)}")
            else:
                st.warning("Please enter a search query")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions Section - ENHANCED WITH BETTER LAYOUT
    st.markdown("---")
    
    # Status indicator - PRESERVED FROM ORIGINAL
    if transcript_id is None:
        if transcripts:
            st.markdown('<p style="color: #FFFFFF !important; font-size: 2.5rem !important; background: linear-gradient(135deg, rgba(0, 188, 212, 0.1), rgba(0, 180, 216, 0.1)); border-left: 4px solid #00F5FF; border-radius: 6px; padding: 1rem; font-weight: 600;">Selected: All Transcripts (Investigation Insights requires selecting ONE specific transcript)</p>', unsafe_allow_html=True)
    elif isinstance(transcript_id, str):
        try:
            selected_name = next((t['filename'] for t in transcripts if t['id'] == transcript_id), "Unknown")
            st.success(f"Selected: {selected_name} - Ready for Investigation Insights")
        except:
            st.success(f"Selected: 1 transcript - Ready for Investigation Insights")
    
    st.subheader("Quick Actions")
    
    # Create 3 columns for Quick Actions - PRESERVED FUNCTIONALITY
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("DRAMA DETECTION", use_container_width=True):
            with st.spinner("Finding high-drama moments..."):
                try:
                    response = requests.post(
                        f"{colab_url}/drama-detection-ai",
                        json={"min_score": 7.0, "transcript_id": transcript_id},
                        headers={"X-API-Key": "tie_smartco1_demo123"},
                        timeout=120  # PRESERVED 120 SECOND TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        moments = response.json()
                        if moments:
                            st.success(f"Found {len(moments)} high-drama moments")
                            
                            # ENHANCED DRAMA DISPLAY WITH CARDS
                            for m in moments[:5]:
                                drama_score = m.get('drama_score', 0)
                                speaker = m.get('speaker', 'Unknown')
                                intensity = m.get('intensity_level', 'HIGH')
                                
                                # Create drama card with custom HTML
                                st.markdown(f"""
                                <div class="drama-card">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <h3 style="color: #FFFFFF; margin: 0;">{speaker}</h3>
                                        <span class="drama-score">Drama Score: {drama_score:.1f}</span>
                                    </div>
                                    <p style="color: #F0F0F5; margin-top: 10px; font-size: 1.8rem;">
                                        {m.get('exact_quote', '')}
                                    </p>
                                    <div style="display: flex; gap: 20px; margin-top: 15px; color: #999;">
                                        <span>⏰ {m.get('time_code', '00:00:00')}</span>
                                        <span>🔥 {intensity}</span>
                                        <span>📁 {m.get('source_file', 'Unknown')}</span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("No high-drama moments found")
                    else:
                        st.error(f"Drama detection failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("EXTRACT ENTITIES", use_container_width=True):
            with st.spinner("Extracting entities..."):
                try:
                    response = requests.post(
                        f"{colab_url}/entity-extraction",
                        json={"transcript_id": transcript_id},
                        headers={"X-API-Key": "tie_smartco1_demo123"},
                        timeout=30  # PRESERVED 30 SECOND TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        entities = response.json()
                        st.success("Entities extracted successfully")
                        
                        # ENHANCED HORIZONTAL ENTITY DISPLAY WITH CARDS
                        st.markdown("""
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
                        """, unsafe_allow_html=True)
                        
                        # People Card
                        all_people = []
                        for person in entities.get('PERSON_OF_INTEREST', [])[:5]:
                            all_people.append(('👤', person['name'], 'Person'))
                        for suspect in entities.get('SUSPECTS', [])[:3]:
                            all_people.append(('🚨', suspect['name'], 'Suspect'))
                        for victim in entities.get('VICTIMS', [])[:3]:
                            all_people.append(('💔', victim['name'], 'Victim'))
                        
                        if all_people:
                            st.markdown("""
                            <div class="entity-card">
                                <h3 style="color: #10B981; margin-bottom: 15px;">👥 People</h3>
                                <div class="entity-list">
                            """, unsafe_allow_html=True)
                            
                            for emoji, name, type_label in all_people[:10]:
                                st.markdown(f'<span class="entity-item">{emoji} {name}</span>', unsafe_allow_html=True)
                            
                            st.markdown("</div></div>", unsafe_allow_html=True)
                        
                        # Locations Card
                        if entities.get('LOCATIONS'):
                            st.markdown("""
                            <div class="entity-card">
                                <h3 style="color: #A855F7; margin-bottom: 15px;">📍 Locations</h3>
                                <div class="entity-list">
                            """, unsafe_allow_html=True)
                            
                            for location in entities.get('LOCATIONS', [])[:10]:
                                st.markdown(f'<span class="entity-item">📍 {location["name"]}</span>', unsafe_allow_html=True)
                            
                            st.markdown("</div></div>", unsafe_allow_html=True)
                        
                        # Timeline Card
                        if entities.get('TIMELINE'):
                            st.markdown("""
                            <div class="entity-card">
                                <h3 style="color: #0EA5E9; margin-bottom: 15px;">⏰ Timeline</h3>
                                <div class="entity-list">
                            """, unsafe_allow_html=True)
                            
                            for time in entities.get('TIMELINE', [])[:10]:
                                st.markdown(f'<span class="entity-item">⏰ {time["name"]}</span>', unsafe_allow_html=True)
                            
                            st.markdown("</div></div>", unsafe_allow_html=True)
                        
                        # Weapons Card
                        if entities.get('WEAPONS'):
                            st.markdown("""
                            <div class="entity-card">
                                <h3 style="color: #EF4444; margin-bottom: 15px;">🔫 Weapons</h3>
                                <div class="entity-list">
                            """, unsafe_allow_html=True)
                            
                            for weapon in entities.get('WEAPONS', [])[:5]:
                                st.markdown(f'<span class="entity-item">🔫 {weapon["name"]}</span>', unsafe_allow_html=True)
                            
                            st.markdown("</div></div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    else:
                        st.error(f"Entity extraction failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col3:
        # Investigation Insights - PRESERVED LOGIC FROM ORIGINAL
        investigation_enabled = isinstance(transcript_id, str) and transcript_id is not None
        
        if st.button("INVESTIGATION INSIGHTS", use_container_width=True, disabled=not investigation_enabled):
            with st.spinner("AI Detective analyzing case... (This may take a minute)"):
                try:
                    response = requests.post(
                        f"{colab_url}/api/ai-investigation",
                        json={
                            "transcript_id": transcript_id,
                            "focus_area": None,
                            "analysis_depth": "standard"
                        },
                        headers={"X-API-Key": "tie_smartco1_demo123"},
                        timeout=120  # PRESERVED 120 SECOND TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Investigation complete")
                        
                        # ENHANCED INVESTIGATION DISPLAY
                        st.markdown("""
                        <div class="panel" style="margin-top: 20px;">
                            <h2 style="color: #00F5FF; margin-bottom: 20px;">🔍 AI DETECTIVE ANALYSIS</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Analysis content
                        with st.expander("Full Analysis", expanded=True):
                            st.markdown(result.get('analysis', 'No analysis available'))
                            
                            st.markdown("---")
                            st.markdown("**Analysis Statistics:**")
                            meta = result.get('metadata', {})
                            
                            # Create stats grid
                            stats_col1, stats_col2 = st.columns(2)
                            with stats_col1:
                                st.write(f"📄 Statements analyzed: {meta.get('num_statements_analyzed', 'N/A')}")
                                st.write(f"⭐ High-value statements: {meta.get('num_high_value_statements', 'N/A')}")
                            with stats_col2:
                                st.write(f"👥 Entities found: {meta.get('num_entities', 'N/A')}")
                                st.write(f"⚡ Contradictions detected: {meta.get('num_contradictions', 'N/A')}")
                            
                            # Download and Email - PRESERVED FROM ORIGINAL
                            report = f"T!M INVESTIGATION INSIGHTS REPORT\n"
                            report += f"{'='*50}\n\n"
                            report += result.get('analysis', 'No analysis available')
                            report += f"\n\n{'='*50}\n"
                            report += "Analysis Statistics:\n"
                            report += f"- Statements analyzed: {meta.get('num_statements_analyzed', 'N/A')}\n"
                            report += f"- High-value statements: {meta.get('num_high_value_statements', 'N/A')}\n"
                            report += f"- Entities found: {meta.get('num_entities', 'N/A')}\n"
                            report += f"- Contradictions detected: {meta.get('num_contradictions', 'N/A')}\n"
                            
                            col_dl, col_em = st.columns(2)
                            
                            with col_dl:
                                st.download_button(
                                    "Download Investigation Report",
                                    data=report,
                                    file_name=f"T!M_investigation_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            
                            with col_em:
                                inv_email = st.text_input(
                                    "Email to:", 
                                    placeholder="example@email.com",
                                    key=f"inv_email_{datetime.now().timestamp()}"
                                )
                                if st.button("📧 Email Report", use_container_width=True, key=f"send_inv_{datetime.now().timestamp()}"):
                                    if inv_email and "@" in inv_email:
                                        with st.spinner("Sending email..."):
                                            try:
                                                response = requests.post(
                                                    f"{colab_url}/send-email",
                                                    headers={"X-API-Key": "tie_smartco1_demo123"},
                                                    json={
                                                        "recipient": inv_email,
                                                        "subject": "T!M Investigation Report",
                                                        "body": report
                                                    },
                                                    timeout=10
                                                )
                                                if response.status_code == 200:
                                                    st.success(f"✅ Email sent to {inv_email}")
                                                else:
                                                    st.error("Failed to send email")
                                            except Exception as e:
                                                st.error(f"Email error: {str(e)}")
                                    else:
                                        st.warning("Please enter a valid email address")
                    else:
                        st.error(f"Investigation failed: {response.status_code}")
                        try:
                            error_msg = response.json()
                            st.error(f"Error: {error_msg}")
                        except:
                            st.text(f"Response: {response.text[:500]}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        if not investigation_enabled:
            st.caption("Select ONE transcript in the Search section above")

# Footer - PRESERVED FROM ORIGINAL WITH ENHANCED STYLING
st.markdown("---")
st.markdown(
    """
    <div class="footer">
    T!M - Transcript !ntelligence Machine<br>
    REDUCE THE GRIND. REVEAL THE BRILLIANCE.<br>
    © 2025 Ambitious Riff Raff & InSpireWIRE • MVP Demo Version 1.0<br>
    Built for Producers & Editors & ProdCos
    </div>
    """,
    unsafe_allow_html=True
)
