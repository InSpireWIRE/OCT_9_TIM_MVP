import streamlit as st
import requests
import json
import csv
import io
import time
from datetime import datetime

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

# ENHANCED CSS WITH YOUR REQUESTED CHANGES
st.markdown("""
<style>
    /* === CORE DARK THEME === */
    .stApp {
        background-color: #0A0A0A;
        color: #FFFFFF;
    }
    
    /* === CUSTOM T!M TITLE WITH CYAN ! === */
    .custom-title {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -1px;
        border-bottom: 3px solid #00bcd4;
        padding-bottom: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .custom-title .cyan-exclamation {
        color: #00bcd4;
    }
    
    /* === HEADER STYLING === */
    h1 {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -1px;
        border-bottom: 3px solid #00bcd4;
        padding-bottom: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* TAGLINE - LARGER */
    .tagline {
        color: #00bcd4;
        font-size: 3rem !important;
        font-weight: 700;
        letter-spacing: 3px;
        margin: 1rem 0;
        text-transform: uppercase;
    }
    
    /* VERSION - HALF AS LARGE = 2.25rem */
    .version {
        color: #999999;
        font-size: 2.25rem !important;
        font-weight: 700;
        margin-bottom: 2rem;
        line-height: 1.2;
    }
    
    /* === SECTION HEADERS - 1/3 SMALLER = 2rem === */
    h2 {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 2rem !important;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
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
    
    /* RADIO OPTIONS - WHITE */
    .stRadio > div {
        background-color: #1A1A1A;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid #333333;
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
    
    /* === INPUT FIELDS - BLACK TEXT IN WHITE BOX === */
    .stTextInput > div > div > input {
        background-color: #FFFFFF;
        border: 2px solid #00bcd4;
        border-radius: 8px;
        padding: 1rem;
        color: #000000 !important;
        font-size: 1.33rem !important;
        font-weight: 600;
    }
    
    /* === TRANSCRIPT SELECTOR - 1/3 SMALLER === */
    .transcript-selector {
        background-color: #1A1A1A;
        border: 2px solid #00bcd4;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .transcript-button {
        background-color: #1A1A1A;
        border: 2px solid #00bcd4;
        color: #00bcd4;
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
        background-color: #00bcd4;
        color: #0A0A0A;
        transform: translateX(5px);
    }
    
    .transcript-selected {
        background-color: #00bcd4 !important;
        color: #0A0A0A !important;
        font-weight: 800;
    }
    
    /* EXPANDER STYLING - 1/3 SMALLER */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.1), rgba(0, 172, 193, 0.1));
        border-left: 3px solid #00bcd4;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1.67rem !important;
        color: #FFFFFF !important;
        padding: 1rem;
    }
    
    .streamlit-expanderContent {
        background-color: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 0 0 6px 6px;
        padding: 1.5rem;
        font-size: 2rem !important;
        line-height: 1.6;
    }
    
    /* === OUTPUT TEXT - 1/3 SMALLER & WHITE === */
    .streamlit-expanderContent p {
        font-size: 2rem !important;
        line-height: 1.6;
        margin-bottom: 1rem;
        color: #FFFFFF !important;
    }
    
    .streamlit-expanderContent strong {
        color: #00bcd4;
        font-size: 2.07rem !important;
    }
    
    /* === BUTTONS === */
    .stButton > button {
        background: linear-gradient(135deg, #00bcd4, #00acc1);
        color: #0A0A0A;
        border: none;
        padding: 1.5rem 2.5rem;
        font-weight: 700;
        font-size: 3.5rem !important;
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00acc1, #00bcd4);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 188, 212, 0.4);
    }
    
    .stButton > button:disabled {
        background: #333333;
        color: #666666;
        cursor: not-allowed;
        transform: none;
    }
    
    /* === FILE UPLOADER === */
    .stFileUploader {
        background-color: #1A1A1A;
        border: 2px dashed #00bcd4;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader label {
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 2rem !important;
    }
    
    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF;
    }
    
    section[data-testid="stFileUploadDropzone"] small {
        color: #000000 !important;
        font-size: 1.5rem !important;
    }
    
    /* === MESSAGES - WHITE === */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.2), rgba(0, 188, 212, 0.2));
        color: #FFFFFF !important;
        border-left: 4px solid #00FF00;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 700;
        font-size: 2.5rem !important;
    }
    
    .stError {
        background-color: rgba(244, 67, 54, 0.1);
        color: #FFFFFF !important;
        border-left: 4px solid #f44336;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 600;
        font-size: 2.5rem !important;
    }
    
    .stWarning {
        background-color: rgba(255, 152, 0, 0.1);
        color: #FFFFFF !important;
        border-left: 4px solid #ff9800;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 600;
        font-size: 2.5rem !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.1), rgba(0, 180, 216, 0.1));
        color: #FFFFFF !important;
        border-left: 4px solid #00bcd4;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 600;
        font-size: 2.5rem !important;
    }
    
    /* === DOWNLOAD BUTTONS === */
    .stDownloadButton > button {
        background-color: #1A1A1A;
        border: 2px solid #00bcd4;
        color: #00bcd4;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 2rem !important;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background-color: #00bcd4;
        color: #0A0A0A;
    }
    
    /* === CONNECTION STATUS === */
    .connection-status-green {
        background: linear-gradient(135deg, #00FF00, #00d900);
        color: #0A0A0A;
        font-weight: 900;
        font-size: 1.5rem !important;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-align: center;
        border: 2px solid #00FF00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.4);
    }

    .connection-status-red {
        background: linear-gradient(135deg, #ff5252, #f44336);
        color: #FFFFFF;
        font-weight: 900;
        font-size: 1.5rem !important;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-align: center;
        border: 2px solid #ff5252;
        box-shadow: 0 0 15px rgba(255, 82, 82, 0.4);
    }
    
    /* === FOOTER === */
    .footer {
        text-align: center;
        color: #999999;
        font-size: 1.5rem !important;
        padding: 2rem 0;
        margin-top: 4rem;
        border-top: 2px solid #333333;
    }
    
    /* === ALL TEXT WHITE & READABLE === */
    p, div, span, label {
        color: #FFFFFF !important;
        font-size: 2rem !important;
    }
    
    /* Caption text for disabled button */
    .stCaption {
        color: #FFFFFF !important;
        font-size: 1.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="T!M - Transcript !ntelligence Machine", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'selected_transcript_id' not in st.session_state:
    st.session_state.selected_transcript_id = None
if 'selected_transcript_name' not in st.session_state:
    st.session_state.selected_transcript_name = None

# Header with Cyan ! in T!M
st.markdown('<h1 class="custom-title">T<span class="cyan-exclamation">!</span>M - Transcript <span class="cyan-exclamation">!</span>ntelligence Machine</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">REDUCE THE GRIND. REVEAL THE BRILLIANCE.</p>', unsafe_allow_html=True)
st.markdown('<p class="version">MVP Demo Version 1.0</p>', unsafe_allow_html=True)

# Connection section
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
    # Upload and Search Side-by-Side
    st.markdown("---")
    
    upload_col, search_col = st.columns([1, 2])
    
    # UPLOAD SECTION WITH 360 SECOND TIMEOUT
    with upload_col:
        st.subheader("Upload Transcript")
        uploaded_file = st.file_uploader(
            "Choose a transcript file",
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
                            timeout=360  # 360 SECONDS = 6 MINUTES
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
    
    # SEARCH SECTION
    with search_col:
        st.subheader("Search Transcripts")
        
        search_type = st.radio(
            "Search Method",
            ["Keyword Search", "Semantic Search (AI)"],
            help="Keyword: Exact matching | Semantic: AI understands meaning"
        )
        
        # Get transcript list
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
        
        # NEW TRANSCRIPT SELECTOR WITH EXPANDER
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
                
                if st.session_state.selected_transcript_name:
                    st.success(f"Selected: {st.session_state.selected_transcript_name}")
                    transcript_id = st.session_state.selected_transcript_id
                    
                    # ADD DELETE BUTTON HERE
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button("🗑️ Delete", key="delete_transcript", 
                                    help="Delete this transcript permanently"):
                            
                            # Confirmation dialog
                            if 'confirm_delete' not in st.session_state:
                                st.session_state.confirm_delete = False
                            
                            if st.session_state.confirm_delete:
                                st.error("⚠️ Are you SURE? This cannot be undone!")
                                col_yes, col_no = st.columns(2)
                                
                                with col_yes:
                                    if st.button("Yes, DELETE", key="confirm_yes"):
                                        if transcript_id:
                                            try:
                                                # Call delete endpoint
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
                                                    # Clear session state
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
                                st.session_state.confirm_delete = True
                                st.rerun()
        else:
            st.warning("No transcripts found. Upload a transcript first.")
        
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
                            f"{colab_url}{endpoint}",  # Use the endpoint variable defined above
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
                                
                                # Download results section
                                if results:
                                    st.markdown("---")
                                    st.subheader("Download Results")
                                    dcol1, dcol2, dcol3 = st.columns(3)
                                    
                                    with dcol1:
                                        # CSV Download
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
                                        # Text Report Download
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
                                        # Email Results
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
    
    # Quick Actions Section
    st.markdown("---")
    
    # Status indicator for Investigation Insights - NOW WHITE
    if transcript_id is None:
        if transcripts:
            st.markdown('<p style="color: #FFFFFF !important; font-size: 2.5rem !important; background: linear-gradient(135deg, rgba(0, 188, 212, 0.1), rgba(0, 180, 216, 0.1)); border-left: 4px solid #00bcd4; border-radius: 6px; padding: 1rem; font-weight: 600;">Selected: All Transcripts (Investigation Insights requires selecting ONE specific transcript)</p>', unsafe_allow_html=True)
    elif isinstance(transcript_id, str):
        try:
            selected_name = next((t['filename'] for t in transcripts if t['id'] == transcript_id), "Unknown")
            st.success(f"Selected: {selected_name} - Ready for Investigation Insights")
        except:
            st.success(f"Selected: 1 transcript - Ready for Investigation Insights")
    
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("DRAMA DETECTION", use_container_width=True):
            with st.spinner("Finding high-drama moments..."):
                try:
                    response = requests.post(
                        f"{colab_url}/drama-detection-ai",
                        json={"min_score": 7.0, "transcript_id": transcript_id},
                        headers={"X-API-Key": "tie_smartco1_demo123"},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        moments = response.json()
                        if moments:
                            st.success(f"Found {len(moments)} high-drama moments")
                            
                            for m in moments[:5]:
                                drama_score = m.get('drama_score', 0)
                                speaker = m.get('speaker', 'Unknown')
                                intensity = m.get('intensity_level', 'HIGH')
                                
                                with st.expander(f"{speaker} - Drama Score: {drama_score:.1f}"):
                                    st.write(f"**Quote:** {m.get('exact_quote', '')}")
                                    st.write(f"**Time:** {m.get('time_code', '00:00:00')}")
                                    st.write(f"**Intensity Level:** {intensity}")
                                    st.write(f"**Source:** {m.get('source_file', 'Unknown')}")
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
                        json={"transcript_id": transcript_id},  # Pass transcript_id
                        headers={"X-API-Key": "tie_smartco1_demo123"},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        entities = response.json()
                        st.success("Entities extracted successfully")
                        
                        # Display entities in 4 columns
                        ecol1, ecol2, ecol3, ecol4 = st.columns(4)
                        
                        with ecol1:
                            st.markdown("**People**")
                            all_people = []
                            for person in entities.get('PERSON_OF_INTEREST', [])[:5]:
                                all_people.append(f"• {person['name']}")
                            for suspect in entities.get('SUSPECTS', [])[:3]:
                                all_people.append(f"• {suspect['name']} (Suspect)")
                            for victim in entities.get('VICTIMS', [])[:3]:
                                all_people.append(f"• {victim['name']} (Victim)")
                            
                            for p in all_people[:10]:
                                st.write(p)
                        
                        with ecol2:
                            st.markdown("**Locations**")
                            for location in entities.get('LOCATIONS', [])[:10]:
                                st.write(f"• {location['name']}")
                        
                        with ecol3:
                            st.markdown("**Timeline**")
                            for time in entities.get('TIMELINE', [])[:10]:
                                st.write(f"• {time['name']}")
                        
                        with ecol4:
                            st.markdown("**Weapons**")
                            for weapon in entities.get('WEAPONS', [])[:5]:
                                st.write(f"• {weapon['name']}")
                    else:
                        st.error(f"Entity extraction failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col3:
        # Investigation Insights - only enabled if single transcript selected
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
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Investigation complete")
                        
                        with st.expander("AI DETECTIVE ANALYSIS", expanded=True):
                            st.markdown(result.get('analysis', 'No analysis available'))
                            
                            st.markdown("---")
                            st.markdown("**Analysis Statistics:**")
                            meta = result.get('metadata', {})
                            st.write(f"- Statements analyzed: {meta.get('num_statements_analyzed', 'N/A')}")
                            st.write(f"- High-value statements: {meta.get('num_high_value_statements', 'N/A')}")
                            st.write(f"- Entities found: {meta.get('num_entities', 'N/A')}")
                            st.write(f"- Contradictions detected: {meta.get('num_contradictions', 'N/A')}")
                            
                            # Download Investigation Report
                            report = f"T!M INVESTIGATION INSIGHTS REPORT\n"
                            report += f"{'='*50}\n\n"
                            report += result.get('analysis', 'No analysis available')
                            report += f"\n\n{'='*50}\n"
                            report += "Analysis Statistics:\n"
                            report += f"- Statements analyzed: {meta.get('num_statements_analyzed', 'N/A')}\n"
                            report += f"- High-value statements: {meta.get('num_high_value_statements', 'N/A')}\n"
                            report += f"- Entities found: {meta.get('num_entities', 'N/A')}\n"
                            report += f"- Contradictions detected: {meta.get('num_contradictions', 'N/A')}\n"
                            
                            # Email functionality for Investigation Report
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

# Footer
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