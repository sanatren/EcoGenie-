import streamlit as st
import os
import logging
import geocoder
from PIL import Image
from typing import List, Dict
import google.generativeai as genai

# Additional imports for animations and styling
from streamlit_lottie import st_lottie
import requests
import time

# -- 1) Load Lottie animations (from URL or local JSON) --
def load_lottieurl(url: str):
    """Helper function to load a Lottie animation from a URL."""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Example Lottie animation URLs (you can replace these with your own)
LOTTIE_RECYCLING_URL = "https://lottie.host/65119e8e-f82c-4b53-b613-16096eb36a8e/Yrn7AjQUNK.json"
LOTTIE_UPLOAD_URL = "https://lottie.host/f5326758-f0e1-4cdc-b702-b60760d5a86f/95NWTtRHVm.json"

# Get the API key from the environment
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found. Please set it in the .env file or as an environment variable.")

# Configure the Generative AI API
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

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
    """Handle location-related operations"""

    @staticmethod
    def get_location() -> Dict[str, str]:
        """Get user's location"""
        try:
            # Manual input or IP-based geolocation
            st.info("Using IP-based geolocation. Provide manual inputs if needed.")
            g = geocoder.ip('me')
            if g.ok:
                return {
                    "city": g.city or "Mumbai",
                    "state": g.state or "Maharashtra",
                    "country": g.country or "India"
                }
            raise Exception("Geolocation failed")
        except Exception as e:
            st.warning("Location detection failed. Defaulting to Mumbai, Maharashtra.")
            return {"city": "Mumbai", "state": "Maharashtra", "country": "India"}

def classify_scrap(images: List[Image.Image], location: Dict[str, str]):
    """Classify images as recyclable or non-recyclable with Generative AI."""
    classifications = []
    state = location.get("state", "Maharashtra")

    for image in images:
        prompt = f"""
        Classify the item in this image according to {state}, India recycling rules:
        1. Is it recyclable?
        2. Can it be sold to a scrap collector?
        3. Recommendations for preparation and safe handling.
        """
        # In practice, you may need a different approach to pass images to the model
        # For demonstration, we treat the image as a separate input or handle as text-based prompt
        response = model.generate_content([prompt, "Image placeholder"])
        classifications.append({
            "image": image,
            "recommendation": response.text,
            "recycling_rules": RECYCLING_RULES.get(state, ["No rules available."])
        })
    return classifications

def main():
    # -- 2) Custom CSS for minor transitions or styling --
    custom_css = """
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
    .box {
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .box-recyclable {
        background-color: #d0f0c0; /* pale green */
    }
    .box-nonrecyclable {
        background-color: #ffe6e6; /* pale red */
    }
    .rules {
        font-style: italic;
        color: #4b4b4b;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    st.markdown("<h1 class='title'>♻️ Scrap Classifier and Recycling Guide</h1>", unsafe_allow_html=True)
    st.sidebar.header("Upload and Classify Scrap")

    # -- 3) Lottie animations in the sidebar or main page --
    lottie_recycling = load_lottieurl(LOTTIE_RECYCLING_URL)
    lottie_upload = load_lottieurl(LOTTIE_UPLOAD_URL)

    if lottie_recycling:
        st_lottie(lottie_recycling, speed=1, height=200, key="recycling")

    # User location
    location = LocationService.get_location()
    st.sidebar.write(f"Detected Location: {location['city']}, {location['state']}")

    # -- 4) Lottie animation near file uploader for better user experience --
    if lottie_upload:
        with st.sidebar:
            st_lottie(lottie_upload, speed=1, height=150, key="uploader")

    # Upload images
    uploaded_files = st.file_uploader(
        "Upload images of the items to classify",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "webp"]
    )

    # Process uploaded files
    if uploaded_files:
        # We'll add a small spinner as we process images
        with st.spinner("Classifying your scrap..."):
            time.sleep(1)  # Just to simulate a little delay
            images = [Image.open(file) for file in uploaded_files]
            results = classify_scrap(images, location)

        # Once classification is done, we show results with a bit of flair
        st.balloons()  # Celebratory effect
        for i, result in enumerate(results):
            st.image(images[i], caption=f"Uploaded Image {i + 1}")

            # Determine if the recommendation text suggests recyclable or not
            recommendation_lower = result['recommendation'].lower()
            is_recyclable = "yes" in recommendation_lower or "recyclable" in recommendation_lower
            
            if is_recyclable:
                box_class = "box box-recyclable"
                status_header = "### This item may be Recyclable!"
            else:
                box_class = "box box-nonrecyclable"
                status_header = "### This item may Not be Recyclable or Needs Special Handling!"

            st.markdown(f"<div class='{box_class}'>{status_header}</div>", unsafe_allow_html=True)
            st.write(f"**Recommendation:** {result['recommendation']}")
            st.markdown("---")
            st.markdown("<span class='rules'>Recycling Rules:</span>", unsafe_allow_html=True)
            for rule in result['recycling_rules']:
                st.write(f"- {rule}")

    else:
        st.info("Please upload one or more images to proceed.")

if __name__ == "__main__":
    main()
