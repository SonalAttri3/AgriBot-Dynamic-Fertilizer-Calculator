import streamlit as st
import pandas as pd
import re
import os

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="AgriBot - Fertilizer Assistant",
    page_icon="🌱",
    layout="centered"
)

# --- 2. Sidebar: Data Upload & Reset ---
st.sidebar.header("📂 Data Management")
st.sidebar.markdown("Upload your own CSV files to override the defaults.")

# File Uploaders
uploaded_crop_file = st.sidebar.file_uploader("Upload Crop Requirements (C1.csv)", type="csv")
uploaded_dist_file = st.sidebar.file_uploader("Upload District Data (Fdistrict.csv)", type="csv")

# Clear Cache Button (Helps fix "stuck" errors)
if st.sidebar.button("🔄 Reset / Clear Cache"):
    st.cache_data.clear()
    st.rerun()

# --- 3. Load and Preprocess Data ---
# Renamed function to 'v2' to force Streamlit to refresh the cache and fix the error
@st.cache_data
def load_data_v2(crop_source, dist_source):
    """
    Loads data from either a file path (string) or an uploaded file object.
    Returns exactly 3 values: df_crop, df_dist, error_message
    """
    try:
        # Load datasets
        # We assume the format matches the original files (Header on 2nd row, so skiprows=1)
        # If your files have headers on row 1, change this to skiprows=0
        c1 = pd.read_csv(crop_source, skiprows=1)
        f_dist = pd.read_csv(dist_source, skiprows=1)
        
        # Clean column names (strip whitespace)
        c1.columns = c1.columns.str.strip()
        f_dist.columns = f_dist.columns.str.strip()
        
        # Normalize text data for easier searching
        if 'crop' in c1.columns:
            c1['crop_lower'] = c1['crop'].astype(str).str.lower().str.strip()
        
        if 'district' in f_dist.columns and 'state' in f_dist.columns:
            f_dist['district_lower'] = f_dist['district'].astype(str).str.lower().str.strip()
            f_dist['state_lower'] = f_dist['state'].astype(str).str.lower().str.strip()
        
        # SUCCESS: Return 3 values (None for error)
        return c1, f_dist, None 
    except Exception as e:
        # FAILURE: Return 3 values (None for dfs, string for error)
        return None, None, str(e)

# Determine which source to use (Uploaded or Default)
crop_input = uploaded_crop_file if uploaded_crop_file is not None else 'C1.csv'
dist_input = uploaded_dist_file if uploaded_dist_file is not None else 'Fdistrict.csv'

# Check if files exist (only if using defaults)
if isinstance(crop_input, str) and not os.path.exists(crop_input):
    df_crop, df_dist, error_msg = None, None, "Default 'C1.csv' file missing."
elif isinstance(dist_input, str) and not os.path.exists(dist_input):
    df_crop, df_dist, error_msg = None, None, "Default 'Fdistrict.csv' file missing."
else:
    # Load the data
    df_crop, df_dist, error_msg = load_data_v2(crop_input, dist_input)

# Handle Loading Errors & Display Warnings
if error_msg:
    if uploaded_crop_file or uploaded_dist_file:
         st.error(f"Error reading your file: {error_msg}")
         st.info("Tip: Ensure your uploaded CSV has the header on the 2nd row (skiprows=1).")
    else:
         st.warning("⚠️ Waiting for data. Please upload 'C1.csv' and 'Fdistrict.csv' in the sidebar.")
elif df_crop is None or df_dist is None:
    st.warning("⚠️ Data could not be loaded. Please check your files.")

# --- 4. Logic & Calculation Functions ---

def get_crop_n_req(crop_name):
    """Extracts average N requirement for a crop."""
    if df_crop is None: return None
    
    # Flexible matching
    row = df_crop[df_crop['crop_lower'] == crop_name]
    if row.empty:
        return None
    
    val = row.iloc[0]['N(kg/ha)']
    # Handle ranges like "100-120"
    if '-' in str(val):
        low, high = map(float, val.split('-'))
        return (low + high) / 2
    try:
        return float(val)
    except:
        return None

def get_soil_n_data(district, state):
    """Extracts soil N data for a specific district and state."""
    if df_dist is None: return None
    
    mask = (df_dist['district_lower'] == district) & (df_dist['state_lower'] == state)
    row = df_dist[mask]
    
    if row.empty:
        return None
    return row.iloc[0]['Avg. soil N(kg/ha)']

def calculate_reduction(district, state, crop):
    """Main logic to calculate urea reduction."""
    n_req = get_crop_n_req(crop)
    if n_req is None:
        return f"❌ I couldn't find nutrient requirements for **{crop.title()}**."
    
    soil_n = get_soil_n_data(district, state)
    if soil_n is None:
        return f"❌ I couldn't find soil data for **{district.title()}** in **{state.title()}**."
    
    excess_n = soil_n - n_req
    # Urea is 46% Nitrogen
    potential_savings = excess_n / 0.46
    
    response = (
        f"### 🌾 Analysis for {crop.title()} in {district.title()}, {state.title()}\n\n"
        f"**1. Crop Requirement:** {crop.title()} needs approx **{n_req:.1f} kg/ha** of Nitrogen.\n"
        f"**2. Soil Status:** Your soil already has **{soil_n:.1f} kg/ha** of Nitrogen.\n"
        f"**3. Excess Nitrogen:** You have an excess of **{excess_n:.1f} kg/ha**.\n\n"
        f"#### 📉 Recommendation:\n"
        f"You can potentially reduce Urea application by **{potential_savings:.2f} kg/ha** "
        f"while still meeting the crop's needs."
    )
    return response

def parse_input(user_text):
    if df_crop is None or df_dist is None: return {}
    
    user_text = user_text.lower()
    found = {}
    
    # Check for Crops
    if 'crop_lower' in df_crop.columns:
        all_crops = df_crop['crop_lower'].dropna().unique()
        for c in all_crops:
            # Match whole words to avoid partial matches
            if re.search(r'\b' + re.escape(c) + r'\b', user_text):
                found['crop'] = c
                break 
            
    # Check for Districts
    if 'district_lower' in df_dist.columns:
        all_districts = df_dist['district_lower'].dropna().unique()
        for d in all_districts:
            if re.search(r'\b' + re.escape(d) + r'\b', user_text):
                found['district'] = d
                break
            
    # Check for States
    if 'state_lower' in df_dist.columns:
        all_states = df_dist['state_lower'].dropna().unique()
        for s in all_states:
            if re.search(r'\b' + re.escape(s) + r'\b', user_text):
                found['state'] = s
                break
            
    # Auto-infer state if district is unique
    if 'district' in found and 'state' not in found:
        possible_states = df_dist[df_dist['district_lower'] == found['district']]['state_lower'].unique()
        if len(possible_states) == 1:
            found['state'] = possible_states[0]
            
    return found

# --- 5. Chat Interface Layout ---

st.title("🌱 AgriBot")
st.markdown("I can help you calculate fertilizer reductions based on your soil health.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am ready. Try asking: *'Plan for Rice in Ludhiana'*"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. Chat Logic ---

if prompt := st.chat_input("Type here... (e.g., 'Check Wheat for Hisar')"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            entities = parse_input(prompt)
            
            district = entities.get('district')
            state = entities.get('state')
            crop = entities.get('crop')
            
            response_text = ""
            
            if df_crop is None or df_dist is None:
                 response_text = "⚠️ **System Error:** Data is not loaded. Please upload CSV files in the sidebar."
            elif district and state and crop:
                response_text = calculate_reduction(district, state, crop)
            elif district and crop and not state:
                 response_text = f"I found **{district.title()}**, but I need to know the **State** as well. (e.g., Ludhiana, Punjab)"
            elif not district and not crop:
                response_text = "I couldn't identify the location or crop. Please use the format: **'Crop in District'** (e.g., *Rice in Ludhiana*)."
            elif not district:
                response_text = "Which **District** are you asking about?"
            elif not crop:
                response_text = f"I found **{district.title()}**. Which **Crop** are you planning to grow?"
            else:
                 response_text = "I'm having trouble understanding. Please try: *'Plan for Rice in Ludhiana, Punjab'*."

            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- Sidebar: Database Status ---
with st.sidebar:
    st.divider()
    st.header("📊 Database Status")
    if df_crop is not None:
        st.success(f"✅ Crops Loaded: {len(df_crop)}")
        st.dataframe(df_crop.head(3), hide_index=True)
    else:
        st.error("❌ Crops Data Missing")
    
    if df_dist is not None:
        st.success(f"✅ Districts Loaded: {len(df_dist)}")
        st.dataframe(df_dist.head(3), hide_index=True)
    else:
        st.error("❌ District Data Missing")