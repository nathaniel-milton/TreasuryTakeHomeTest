import streamlit as st
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI  # Or anthropic, google-genai depending on your API choice

load_dotenv()

load_dotenv()

# Initialize API Client
client = OpenAI()

st.set_page_config(page_title="TTB Label Verification Prototype", page_icon="🍾", layout="wide")

# Custom Styling for "Dave-proof" UI
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .stAlert { margin-top: 10px; }
    </style>
""", unsafe_allowed_code=html)

## Header Section
st.title("🍾 AI-Powered Alcohol Label Verification")
st.write("Upload label artwork to automatically match text against expected application data.")
st.markdown("---")

def analyze_label_image(image_bytes):
    """Sends image to Vision LLM to extract data fields and check formatting."""
    import base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    prompt = """
    You are a strict TTB Compliance Verification AI. Analyze the provided image of an alcohol beverage label.
    Extract the following fields accurately. If a field is missing, return null.
    
    CRITICAL WARNING STATEMENT CHECK:
    Look for the text 'GOVERNMENT WARNING:'. 
    1. Is it in ALL CAPITAL LETTERS? (true/false)
    2. Is it in BOLD font relative to the surrounding text? (true/false)
    3. Does the text exactly match the federal warning statement? (true/false)

    Return ONLY a valid JSON object matching this structure exactly:
    {
        "brand_name": "extracted string",
        "class_type": "extracted string",
        "alcohol_content": "extracted string",
        "net_contents": "extracted string",
        "warning_all_caps": true/false,
        "warning_bold": true/false,
        "warning_exact_match": true/false,
        "raw_warning_text": "extracted text"
    }
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Highly cost-effective and sub-3-second responses
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ],
            }
        ],
        temperature=0.0
    )
    return json.loads(response.choices[0].message.content)

def compare_fields(extracted, expected):
    """Performs soft matching logic allowing minor case variations but flagging discrepancies."""
    if not extracted or not expected:
        return "⚠️ Missing Data", "orange"
    if str(extracted).strip().lower() == str(expected).strip().lower():
        if str(extracted).strip() != str(expected).strip():
            return "✅ Match (Case Mismatch)", "green"
        return "✅ Pass", "green"
    return "❌ Mismatch", "red"

# Mock Application database to simulate form data input
expected_data = {
    "brand_name": "OLD TOM DISTILLERY",
    "class_type": "Kentucky Straight Bourbon Whiskey",
    "alcohol_content": "45% Alc./Vol. (90 Proof)",
    "net_contents": "750 mL"
}

## Sidebar for Application Form Data Input (Simulating COLA data entry)
with st.sidebar:
    st.header("📋 Expected Application Data")
    st.caption("Simulates data pulled from the COLA application form.")
    app_brand = st.text_input("Brand Name", expected_data["brand_name"])
    app_class = st.text_input("Class / Type", expected_data["class_type"])
    app_abv = st.text_input("Alcohol Content", expected_data["alcohol_content"])
    app_size = st.text_input("Net Contents", expected_data["net_contents"])

## Main UI: Mode Selection (Addressing Janet's request for batch uploads)
mode = st.radio("Select Upload Mode:", ["Single Label Review", "Batch Processing (Importers)"], horizontal=True)

if mode == "Single Label Review":
    uploaded_file = st.file_uploader("Choose a label image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.image(uploaded_file, caption='Uploaded Label Artwork', use_container_width=True)
            
        with col2:
            st.subheader("Verification Matrix")
            start_time = time.time()
            
            with st.spinner('AI analysis in progress (Target < 5s)...'):
                try:
                    # Execute AI extraction
                    extracted = analyze_label_image(uploaded_file.getvalue())
                    processing_time = time.time() - start_time
                    
                    # Layout comparison table
                    fields = [
                        ("Brand Name", app_brand, extracted.get("brand_name")),
                        ("Class/Type", app_class, extracted.get("class_type")),
                        ("Alcohol Content", app_abv, extracted.get("alcohol_content")),
                        ("Net Contents", app_size, extracted.get("net_contents")),
                    ]
                    
                    # Display Match/Mismatch Metrics
                    for field_name, exp_val, ext_val in fields:
                        status, color = compare_fields(ext_val, exp_val)
                        st.markdown(f"**{field_name}**: Form: `{exp_val}` | Label: `{ext_val}` -> :{color}[{status}]")
                    
                    st.markdown("---")
                    st.subheader("⚠️ Government Warning Checklist")
                    
                    # Strict formatting checks requested by Jenny
                    w_caps = extracted.get("warning_all_caps", False)
                    w_bold = extracted.get("warning_bold", False)
                    w_match = extracted.get("warning_exact_match", False)
                    
                    st.markdown(f"{'✅' if w_caps else '❌'} **'GOVERNMENT WARNING:' in All-Caps**")
                    st.markdown(f"{'✅' if w_bold else '❌'} **'GOVERNMENT WARNING:' is Bolded**")
                    st.markdown(f"{'✅' if w_match else '❌'} **Text Matches Federal Mandate Word-for-Word**")
                    
                    if not (w_caps and w_bold and w_match):
                        st.error("Compliance Alert: Government Warning formatting violations detected.")
                    else:
                        st.success("Government Warning format verified successfully.")
                        
                    st.caption(f"Processing time: {processing_time:.2f} seconds (Target: 5.0s)")
                    
                    # Final human override action buttons (Dave-friendly)
                    st.markdown("---")
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        st.button("👍 Approve Application", type="primary", use_container_width=True)
                    with col_btn2:
                        st.button("👎 Reject & Flag Errors", type="secondary", use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")

else:
    # Batch Processing Mode
    uploaded_files = st.file_uploader("Upload multiple label images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        st.subheader(f"Batch Processing Queue ({len(uploaded_files)} items)")
        
        # Displaying a neat overview table for high throughput
        results_list = []
        for file in uploaded_files:
            with st.spinner(f'Processing {file.name}...'):
                try:
                    res = analyze_label_image(file.getvalue())
                    # Fast dummy matching for structural view
                    brand_status, _ = compare_fields(res.get("brand_name"), app_brand)
                    warn_status = "Pass" if (res.get("warning_all_caps") and res.get("warning_bold")) else "Fail"
                    
                    results_list.append({
                        "File Name": file.name,
                        "Extracted Brand": res.get("brand_name"),
                        "Brand Match": brand_status,
                        "Warning Check": warn_status
                    })
                except:
                    results_list.append({"File Name": file.name, "Extracted Brand": "Error", "Brand Match": "Error", "Warning Check": "Error"})
                    
        st.table(results_list)
        st.success("Batch processing complete!")
