import streamlit as st
import os
import logging
import requests
import time
import google.generativeai as genai
from PIL import Image
from typing import List, Dict
from streamlit_lottie import st_lottie
from streamlit_bokeh_events import streamlit_bokeh_events
from geopy.geocoders import Nominatim
from bokeh.models import CustomJS

# Lottie animations
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

LOTTIE_RECYCLING_URL = "https://lottie.host/65119e8e-f82c-4b53-b613-16096eb36a8e/Yrn7AjQUNK.json"
LOTTIE_UPLOAD_URL = "https://lottie.host/f5326758-f0e1-4cdc-b702-b60760d5a86f/95NWTtRHVm.json"

# Configure API
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found. Please set it in the .env file or as an environment variable.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Recycling rules dictionary remains the same as in your original code
RECYCLING_RULES = {
    "Maharashtra": [
        "Separate waste at source into wet, dry, and hazardous categories.",
        "Ensure plastics are clean and dry before disposal.",
        "E-waste should be disposed of through authorized e-waste collection centers.",
        "Use bins provided by local authorities for proper segregation."
    ],
    "Delhi": [
        "Use separate bins for dry waste (plastic, paper, metal) and wet waste (food scraps).",
        "Compost kitchen waste to reduce landfill burden.",
        "Recycle paper products and avoid mixing recyclables with non-recyclables.",
        "Participate in local clean-up drives and awareness programs."
    ],
    "Karnataka": [
        "Sort waste into dry and wet categories at home before disposal.",
        "Use designated collection bins for e-waste and ensure safe disposal.",
        "Encourage local recycling initiatives and community clean-ups.",
        "Ensure that plastic containers are rinsed and cleaned before recycling."
    ],
    "Tamil Nadu": [
        "Rinse all plastic bottles and containers before disposal.",
        "Separate recyclable materials (metals, plastics, paper) from non-recyclables.",
        "Participate in local waste segregation workshops.",
        "Avoid single-use plastics and prefer biodegradable options."
    ],
    "West Bengal": [
        "Recyclables should be clean and dry; food residue can contaminate materials.",
        "E-waste must be collected and disposed of through authorized channels.",
        "Use community recycling drives to promote awareness.",
        "Segregate hazardous waste (batteries, chemicals) separately."
    ],
    "Gujarat": [
        "Flatten cardboard boxes to save space in recycling bins.",
        "Avoid the use of plastic bags; use cloth bags instead.",
        "Participate in local recycling programs and educational initiatives.",
        "Dispose of electronic waste at designated centers only."
    ],
    "Rajasthan": [
        "Source segregation of waste into biodegradable and non-biodegradable materials.",
        "Participate in community awareness programs about recycling.",
        "Ensure waste is dry and clean before disposal in recycling bins.",
        "Compost organic waste at home to reduce landfill use."
    ],
    "Andhra Pradesh": [
        "Recyclables should be kept dry; wet items can lead to contamination.",
        "Follow local guidelines for electronic waste disposal.",
        "Engage in community-led recycling efforts and campaigns.",
        "Avoid mixing recyclables with general waste."
    ],
    "Telangana": [
        "Use separate bins for recyclables and ensure they are clean.",
        "Participate in local recycling drives and educational workshops.",
        "Check with local authorities about e-waste collection schedules.",
        "Be aware of local regulations regarding hazardous waste disposal."
    ],
    "Uttar Pradesh": [
        "Sort waste at home into recyclables and non-recyclables.",
        "Consult local agencies for the proper disposal of hazardous materials.",
        "Participate in community initiatives for waste management and recycling.",
        "Use recyclable materials wherever possible to reduce waste."
    ]
}



class LocationService:
    """Handles automatic and manual location selection for Streamlit apps."""

    @staticmethod
    def get_location() -> dict:
        """Fetch user's location automatically using the Geolocation API, 
        with an option for manual selection."""

        DEFAULT_CITY = "Mumbai"
        DEFAULT_STATE = "Maharashtra"
        DEFAULT_COUNTRY = "India"

        # Initialize session state for location
        if "location" not in st.session_state:
            st.session_state.location = {
                "city": DEFAULT_CITY,
                "state": DEFAULT_STATE,
                "country": DEFAULT_COUNTRY
            }
            st.session_state.show_location_picker = True  # Show picker for first-time users

        # Sidebar container for location settings
        location_container = st.sidebar.container()

        # Display current location
        location_container.markdown("### 📍 Your Location")
        location_container.markdown(f"**Current:** {st.session_state.location['city']}, {st.session_state.location['state']}, {st.session_state.location['country']}")

        # Button to trigger location detection
        if location_container.button("📍 Detect My Location"):
            js_code = """
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const coords = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: coords}));
                },
                (error) => {
                    document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {error: error.message}}));
                }
            )
            """

            # Capture the JavaScript result
            result = streamlit_bokeh_events(
                CustomJS(code=js_code),
                events="GET_LOCATION",
                key="get_location",
                refresh_on_update=False,
                override_height=0,
                debounce_time=0
            )

            # DEBUG: Print response from JS
            st.write("DEBUG: Geolocation API Result:", result)  

            if result and "GET_LOCATION" in result:
                location_data = result["GET_LOCATION"]

                if "error" in location_data:
                    st.error(f"Error fetching location: {location_data['error']}")
                else:
                    lat, lon = location_data["latitude"], location_data["longitude"]
                    st.success(f"Your Coordinates: Latitude: {lat}, Longitude: {lon}")

                    # Convert coordinates to a readable address
                    geolocator = Nominatim(user_agent="geoapi")
                    location_info = geolocator.reverse((lat, lon), language="en", exactly_one=True)

                    # DEBUG: Print Reverse Geocoding Response
                    st.write("DEBUG: Reverse Geocoding Response:", location_info.raw if location_info else "No response")

                    if location_info:
                        address_parts = location_info.raw.get("address", {})
                        city = address_parts.get("city", address_parts.get("town", DEFAULT_CITY))
                        state = address_parts.get("state", DEFAULT_STATE)

                        st.success(f"📍 Location updated: {city}, {state}")

                        # Update session state
                        st.session_state.location = {
                            "city": city,
                            "state": state,
                            "country": DEFAULT_COUNTRY
                        }
                        st.rerun()

        # Button to manually change location
        if location_container.button("Change Location Manually"):
            st.session_state.show_location_picker = True

        # Manual selection form
        if st.session_state.get("show_location_picker", False):
            with st.sidebar.form("location_form"):
                st.markdown("### Select Your Location")

                # Popular city selection
                popular_cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune"]
                selected_city = st.radio("Popular Cities", ["Choose City"] + popular_cities)

                # If "Choose City" is selected, allow manual city input
                city = selected_city if selected_city != "Choose City" else st.text_input("Enter City", DEFAULT_CITY)

                # State selection
                state = st.selectbox("Select State", options=["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "West Bengal", "Gujarat", "Rajasthan", "Andhra Pradesh", "Telangana", "Uttar Pradesh"], index=0)

                if st.form_submit_button("Save Location"):
                    st.session_state.location = {
                        "city": city,
                        "state": state,
                        "country": DEFAULT_COUNTRY
                    }
                    st.session_state.show_location_picker = False
                    st.rerun()

        return st.session_state.location

def classify_scrap(images: List[Image.Image], location: Dict[str, str]):
    """Enhanced classification function with more detailed prompts"""
    classifications = []
    state = location.get("state", "Maharashtra")

    for image in images:
        prompt = f"""
This image shows an item the user wishes to sell to a local scrap collector in {state}, India. Based on the object in the image, provide a detailed classification. Specifically, include:

1. **Recyclability**: Clearly state if this item is recyclable based on {state} recycling guidelines.
2. **Scrap Value**: Indicate if it has a resale value and provide a rough range of monetary value (in ₹).
3. **Preparation Steps**: List clear and specific steps to prepare the item for resale or recycling (e.g., cleaning, drying, disassembling).
4. **Safety Guidelines**: Provide actionable safety tips for handling or storing the item.
5. **Environmental Impact**: Explain briefly why recycling this item is important for the environment.

Use a structured format with headings for each section. If a section is not applicable, explicitly say "Not applicable."
"""
        
        response = model.generate_content([prompt, image])
        
        classifications.append({
            "image": image,
            "analysis": response.text,
            "recycling_rules": RECYCLING_RULES.get(state, ["No specific rules available."])
        })
    return classifications

def main():
    # Custom CSS with enhanced styling
    st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 3em;
        color: #008080;
        transition: color 1s ease;
    }
    .title:hover {
        color: #B8860B;
    }
    .result-box {
        padding: 20px;
        margin: 15px 0;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    .category-header {
        color: #2c3e50;
        font-size: 1.2em;
        margin: 10px 0;
    }
    .value-estimate {
        color: #27ae60;
        font-weight: bold;
    }
    .safety-warning {
        color: #e74c3c;
        padding: 10px;
        background-color: #ffebee;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='title'>♻️ Smart Scrap Classifier</h1>", unsafe_allow_html=True)
    
    # Sidebar setup
    st.sidebar.header("Upload and Classify Scrap")
    
    # Location handling
    location = LocationService.get_location()
    st.sidebar.write(f"Active Location: {location['city']}, {location['state']}")
    
    # Display local recycling rules
    with st.expander("View Local Recycling Rules"):
        state_rules = RECYCLING_RULES.get(location['state'], [])
        for rule in state_rules:
            st.write(f"• {rule}")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload images of scrap items",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_files:
        with st.spinner("Analyzing your items..."):
            images = [Image.open(file) for file in uploaded_files]
            results = classify_scrap(images, location)

        st.success("Analysis Complete!")
        st.balloons()

        for i, result in enumerate(results):
            st.markdown(f"### Item {i+1}")
            
            # Create columns for image and analysis
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(images[i], use_column_width=True)
            
            with col2:
                st.markdown(f"<div class='result-box'>{result['analysis']}</div>", 
                          unsafe_allow_html=True)
                
                # Display preparation tips
                if "preparation" in result['analysis'].lower():
                    st.markdown("#### 🔧 Preparation Checklist")
                    st.info(result['analysis'].split("Preparation")[1].split("\n")[0])
                
                # Display safety warnings if present
                if "safety" in result['analysis'].lower():
                    st.markdown("#### ⚠️ Safety Guidelines")
                    st.warning(result['analysis'].split("Safety")[1].split("\n")[0])

            st.markdown("---")

    else:
        # Display welcome message and instructions
        st.info("👋 Welcome! Upload images of your scrap items to get:")
        st.markdown("""
        - ♻️ Recyclability analysis
        - 💰 Potential scrap value
        - 📝 Preparation guidelines
        - ⚠️ Safety recommendations
        - 🌍 Environmental impact
        """)

if __name__ == "__main__":
    main()
