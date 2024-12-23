import streamlit as st
import os
import logging
import geocoder
from PIL import Image
from typing import List, Dict
import google.generativeai as genai
from streamlit_lottie import st_lottie
import requests
import time

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
    "Maharashtra": {
        "rules": [
            "Separate waste at source into wet, dry, and hazardous categories",
            "Ensure plastics are clean and dry before disposal",
            "E-waste should be disposed of through authorized e-waste collection centers",
            "Use bins provided by local authorities for proper segregation"
        ],
        "collection_centers": [
            "Mumbai Municipal Corporation Recycling Centers",
            "Pune Waste Management Facilities",
            "Authorized E-waste Collection Points"
        ],
        "banned_items": [
            "Single-use plastics",
            "Plastic bags below 50 microns",
            "Non-recyclable thermocol"
        ],
        "scrap_rates": {
            "newspaper": "₹12-15 per kg",
            "cardboard": "₹8-10 per kg",
            "metal": "₹30-40 per kg",
            "plastic": "₹15-20 per kg"
        }
    },
    "Delhi": {
        "rules": [
            "Use separate bins for dry waste and wet waste",
            "Compost kitchen waste to reduce landfill burden",
            "Recycle paper products and avoid mixing recyclables",
            "Participate in local clean-up drives"
        ],
        "collection_centers": [
            "MCD Waste Management Centers",
            "Delhi Cantonment Recycling Facilities",
            "Government Authorized Collection Points"
        ],
        "banned_items": [
            "Plastic bags under 50 microns",
            "Non-biodegradable packaging",
            "Disposable plastics"
        ],
        "scrap_rates": {
            "newspaper": "₹13-16 per kg",
            "cardboard": "₹9-11 per kg",
            "metal": "₹32-42 per kg",
            "plastic": "₹16-21 per kg"
        }
    },
    "Karnataka": {
        "rules": [
            "Segregate waste into dry, wet, and reject categories",
            "Hand over e-waste to authorized recyclers",
            "Avoid littering and use public recycling bins",
            "Compost organic waste at home where possible"
        ],
        "collection_centers": [
            "BBMP Dry Waste Collection Centers",
            "Bangalore E-waste Recycling Facilities",
            "State-authorized Hazardous Waste Disposal Units"
        ],
        "banned_items": [
            "Plastic bags below 40 microns",
            "Single-use cutlery",
            "Non-recyclable plastics"
        ],
        "scrap_rates": {
            "newspaper": "₹11-14 per kg",
            "cardboard": "₹7-9 per kg",
            "metal": "₹28-38 per kg",
            "plastic": "₹14-18 per kg"
        }
    },
    "Tamil Nadu": {
        "rules": [
            "Segregate waste at source into biodegradable and non-biodegradable categories",
            "Avoid mixing hazardous waste with household waste",
            "Deposit electronic waste with authorized centers",
            "Participate in local municipal recycling programs"
        ],
        "collection_centers": [
            "Chennai Corporation Recycling Centers",
            "Authorized E-waste Collection Centers in Coimbatore",
            "State-run Waste Management Units"
        ],
        "banned_items": [
            "Plastic bags below 50 microns",
            "Non-recyclable thermocol",
            "Single-use plastics"
        ],
        "scrap_rates": {
            "newspaper": "₹10-13 per kg",
            "cardboard": "₹6-8 per kg",
            "metal": "₹25-35 per kg",
            "plastic": "₹12-17 per kg"
        }
    },
    "Rajasthan": {
        "rules": [
            "Use color-coded bins for waste segregation",
            "Deposit hazardous waste at authorized centers",
            "Recycle plastics and metals through local scrap dealers",
            "Compost kitchen waste to reduce landfill usage"
        ],
        "collection_centers": [
            "Jaipur Waste Processing Centers",
            "Authorized Recycling Centers in Jodhpur",
            "State-run Hazardous Waste Disposal Units"
        ],
        "banned_items": [
            "Plastic carry bags below 50 microns",
            "Disposable polystyrene items",
            "Non-biodegradable packaging"
        ],
        "scrap_rates": {
            "newspaper": "₹12-14 per kg",
            "cardboard": "₹7-10 per kg",
            "metal": "₹30-40 per kg",
            "plastic": "₹14-19 per kg"
        }
    },
    "Uttar Pradesh": {
        "rules": [
            "Segregate waste at source into wet and dry categories",
            "E-waste should be deposited at government-approved facilities",
            "Recycle paper, metal, and glass products",
            "Compost organic waste at home or through municipal programs"
        ],
        "collection_centers": [
            "Lucknow Municipal Recycling Units",
            "Authorized Waste Collection Centers in Kanpur",
            "E-waste Collection Points in Varanasi"
        ],
        "banned_items": [
            "Single-use plastics",
            "Plastic bags below 50 microns",
            "Non-biodegradable materials"
        ],
        "scrap_rates": {
            "newspaper": "₹11-14 per kg",
            "cardboard": "₹8-10 per kg",
            "metal": "₹28-35 per kg",
            "plastic": "₹14-18 per kg"
        }
    },
    "West Bengal": {
        "rules": [
            "Segregate biodegradable and non-biodegradable waste",
            "Recycle plastics, paper, and metals through local dealers",
            "Deposit e-waste at authorized centers",
            "Compost kitchen waste to reduce environmental impact"
        ],
        "collection_centers": [
            "Kolkata Waste Management Facilities",
            "Authorized E-waste Collection Points in Howrah",
            "Municipal Waste Processing Units in Durgapur"
        ],
        "banned_items": [
            "Plastic bags below 50 microns",
            "Non-recyclable thermocol",
            "Disposable plastics"
        ],
        "scrap_rates": {
            "newspaper": "₹12-16 per kg",
            "cardboard": "₹8-11 per kg",
            "metal": "₹30-42 per kg",
            "plastic": "₹15-20 per kg"
        }
    },
    "Gujarat": {
        "rules": [
            "Separate waste into dry and wet categories",
            "Deposit hazardous waste at approved centers",
            "Recycle metals, plastics, and paper responsibly",
            "Use municipal services for e-waste disposal"
        ],
        "collection_centers": [
            "Ahmedabad Dry Waste Collection Centers",
            "Surat Hazardous Waste Disposal Units",
            "Authorized Recycling Points in Vadodara"
        ],
        "banned_items": [
            "Plastic bags below 50 microns",
            "Non-recyclable thermocol items",
            "Single-use plastics"
        ],
        "scrap_rates": {
            "newspaper": "₹13-15 per kg",
            "cardboard": "₹9-12 per kg",
            "metal": "₹32-40 per kg",
            "plastic": "₹16-21 per kg"
        }
    },
    "Punjab": {
        "rules": [
            "Use green and blue bins for waste segregation",
            "Avoid mixing organic and inorganic waste",
            "E-waste should be handed over to authorized centers",
            "Compost kitchen and garden waste at home"
        ],
        "collection_centers": [
            "Chandigarh Recycling Centers",
            "Ludhiana Municipal Waste Facilities",
            "Authorized Scrap Dealers in Amritsar"
        ],
        "banned_items": [
            "Plastic bags below 50 microns",
            "Single-use plastic items",
            "Non-recyclable packaging"
        ],
        "scrap_rates": {
            "newspaper": "₹12-14 per kg",
            "cardboard": "₹7-9 per kg",
            "metal": "₹28-38 per kg",
            "plastic": "₹14-19 per kg"
        }
    },
    "Kerala": {
        "rules": [
            "Segregate waste into biodegradable and non-biodegradable categories",
            "Participate in local recycling initiatives",
            "Deposit hazardous and e-waste at authorized centers",
            "Avoid burning waste materials"
        ],
        "collection_centers": [
            "Thiruvananthapuram Municipal Recycling Units",
            "Authorized Waste Processing Facilities in Kochi",
            "State-run Collection Centers in Kozhikode"
        ],
        "banned_items": [
            "Plastic carry bags below 50 microns",
            "Non-biodegradable thermocol items",
            "Single-use plastics"
        ],
        "scrap_rates": {
            "newspaper": "₹11-15 per kg",
            "cardboard": "₹8-10 per kg",
            "metal": "₹29-37 per kg",
            "plastic": "₹14-18 per kg"
        }
    }
}


class LocationService:
    @staticmethod
    def get_location() -> Dict[str, str]:
        """Get user's location with manual override option"""
        # Add manual location input option in Streamlit
        use_manual = st.sidebar.checkbox("Enter location manually?")
        
        if use_manual:
            city = st.sidebar.text_input("Enter City", "Mumbai")
            state = st.sidebar.selectbox("Select State", 
                                       options=list(RECYCLING_RULES.keys()),
                                       index=0)
            return {
                "city": city,
                "state": state,
                "country": "India"
            }
        
        try:
            st.info("Using IP-based geolocation. Check 'Enter location manually' in sidebar to override.")
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
    """Enhanced classification function with more detailed prompts"""
    classifications = []
    state = location.get("state", "Maharashtra")

    for image in images:
        prompt = f"""
        This image shows an item the user wishes to sell to a local scrap collector in {state}, India. Based on the object in the image, please provide:

        1. Recyclability: Whether this item is recyclable according to {state} recycling guidelines.
        2. Scrap Value: If the item can be sold to a scrap collector and its potential resale value range.
        3. Preparation Steps: Specific steps for preparing this item (cleaning, drying, segregating) to maximize resale value.
        4. Safety Guidelines: Practical advice on safe handling and storage, considering {state} regulations.
        5. Environmental Impact: Brief note on environmental benefits of recycling this item.

        Format the response with clear headings and bullet points.
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
