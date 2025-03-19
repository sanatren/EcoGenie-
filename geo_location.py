import streamlit as st
from streamlit_javascript import st_javascript

def get_browser_location():
    """Get the user's location using the browser's geolocation API"""
    # JavaScript code to get location
    loc_js = """
    async function getLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error("Geolocation not supported"));
            }
            
            navigator.geolocation.getCurrentPosition(
                position => {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    resolve({lat: latitude, lon: longitude});
                },
                error => {
                    reject(error);
                },
                {enableHighAccuracy: true, timeout: 5000, maximumAge: 0}
            );
        });
    }
    
    try {
        const location = await getLocation();
        return location;
    } catch (error) {
        return {"error": error.message};
    }
    """
    
    # Execute the JavaScript code
    try:
        result = st_javascript(loc_js)
        return result
    except Exception as e:
        st.error(f"Error getting location: {str(e)}")
        return None
