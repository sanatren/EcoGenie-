class LocationService:
    @staticmethod
    def get_location() -> dict:
        """Fetch user's location with manual override options."""
        
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
            st.session_state.show_location_picker = False

        # Sidebar container for location settings
        location_container = st.sidebar.container()

        # Display current location
        location_container.markdown("### 📍 Your Location")
        location_container.markdown(f"**Current:** {st.session_state.location['city']}, {st.session_state.location['state']}, {st.session_state.location['country']}")

        # Use a simpler approach than the problematic geolocation
        if location_container.button("Change Location"):
            st.session_state.show_location_picker = True

        # Show manual location selection form if needed
        if st.session_state.get("show_location_picker", False):
            with st.sidebar.form("location_form"):
                st.markdown("### Select Your Location")

                # Predefined cities
                popular_cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune"]
                selected_city = st.radio("Popular Cities", ["Choose City"] + popular_cities)

                city = selected_city if selected_city != "Choose City" else st.text_input("Enter City", DEFAULT_CITY)
                state = st.selectbox("Select State", options=list(RECYCLING_RULES.keys()), index=0)

                if st.form_submit_button("Save Location"):
                    st.session_state.location = {
                        "city": city,
                        "state": state,
                        "country": DEFAULT_COUNTRY
                    }
                    st.session_state.show_location_picker = False
                    st.rerun()

        return st.session_state.location
