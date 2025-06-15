import streamlit as st
import pandas as pd

from utils import (
    initialize_session_state, get_tricks_df, get_completed_tricks
)

# Set page config
st.set_page_config(page_title="Tricky", layout="wide", initial_sidebar_state="collapsed")

# Initialize all required session state
initialize_session_state()

# Load the global data
df_tricks = get_tricks_df()
completed_tricks = get_completed_tricks()

# Main page content (Home page)
def main():

    # Handle trick selection with a callback function
    def store_trick_selection(trick_name, difficulty):
        """Store the selected trick info in session state without navigation"""
        st.session_state.selected_trick = trick_name
        st.session_state.selected_difficulty = difficulty
        st.session_state.redirect_to_page = "pages/Trick_Page.py"

    st.markdown("<h1 style='text-align: center;'>Tricky</h1>", unsafe_allow_html=True)

    # Clear search before rendering input
    if st.session_state.get("clear_search_now"):
        st.session_state.trick_search = ""
        st.session_state.clear_search_now = False
        st.rerun()

    # Modified search container section
    search_container = st.container()
    with search_container:
        st.markdown("<p style='margin-bottom: 0.5rem;'>Search</p>", unsafe_allow_html=True)

        # Create three columns: search input, clear button, and trick data button
        col1, col2, col3 = st.columns([0.3, 1, 0.2])

        with col1:
            search_query = st.text_input("Search for tricks",
                                         placeholder="Enter trick name...",
                                         label_visibility="collapsed",
                                         key="trick_search")

        with col2:
            # Add custom CSS to fix vertical alignment
            st.markdown("""
            <style>
            /* Target the button container */
            [data-testid="stButton"] {
                position: relative;
                top: -16px;  /* Move the button up by 8 pixels */
            }
            </style>
            """, unsafe_allow_html=True)

            if st.button(":material/close:", key="clear_search", help="Clear search"):
                st.session_state.clear_search_now = True
                st.rerun()

        with col3:
            # Apply the same vertical alignment fix
            st.markdown("""
            <style>
            /* Target the trick data button container */
            [data-testid="stButton"]:has(> div:contains("Trick Data")) {
                position: relative;
                top: -16px;  /* Move the button up by 8 pixels */
                float: right;  /* Align to the right */
            }
            </style>
            """, unsafe_allow_html=True)

            if st.button("Trick Data :bar_chart: :material/arrow_forward:", key="trick_data_btn"):
                st.switch_page("pages/Trick_Data.py")

    # Add a thinner separator after the search bar with custom styling
    st.markdown("<hr style='margin-top:0rem; margin-bottom:1.5rem; height:1px'>", unsafe_allow_html=True)

    # Display search results as a full-width category section BEFORE the regular categories
    if 'trick_search' in st.session_state and st.session_state.trick_search:
        search_query = st.session_state.trick_search
        # Filter tricks based on search query
        search_results = df_tricks[df_tricks['Trick'].str.lower().str.contains(search_query.lower())]
        if not search_results.empty:
            st.subheader(f"Search Results for '{search_query}'")
            st.text("")
            # Use the same columns_per_row constant as in the categories display
            columns_per_row = 4

            # Calculate how many rows we need
            num_results = len(search_results)
            num_rows = (num_results + columns_per_row - 1) // columns_per_row

            # Create buttons in rows - same format as in category display
            for row in range(num_rows):
                cols = st.columns(columns_per_row)

                # Add buttons to each column
                for col_idx in range(columns_per_row):
                    result_idx = row * columns_per_row + col_idx

                    # Check if we have a result for this position
                    if result_idx < num_results:
                        trick = search_results.iloc[result_idx]

                        # Check if this trick is completed
                        is_completed = trick['Trick'] in completed_tricks['completed']

                        # Create a centered container for the button
                        with cols[col_idx]:
                            # Create button with trick name and green checkmark if completed
                            button_text = f"{trick['Trick']}"
                            if is_completed:
                                button_text = f"{trick['Trick']} ✅"

                            if st.button(
                                    button_text,
                                    key=f"search_{trick['Trick']}_{trick['Difficulty']}",
                                    use_container_width=True,
                                    on_click=store_trick_selection,
                                    args=(trick['Trick'], trick['Difficulty'])
                            ):
                                pass  # The callback handles the navigation
        else:
            # Show this message if no results found
            st.subheader(f"Search Results for '{search_query}'")
            st.info("No tricks found matching your search.")

        # Add a separator after search results
        st.markdown("---")

    # Add trick type filter
    st.markdown("<p style='margin-bottom: 0.25rem;'>Filter by Trick Type</p>", unsafe_allow_html=True)
    trick_type = st.radio(
        "Show tricks by type:",
        ["All Tricks", "Flip Tricks", "Shove-Its & Spins", "Ollie-Based Tricks", "Other"],
        label_visibility="collapsed",
        horizontal=True
    )

    # Define function to determine trick type based on name
    def get_trick_type(trick_name):
        trick_name_lower = trick_name.lower()

        if 'flip' in trick_name_lower or 'heel' in trick_name_lower:
            return "Flip Tricks"
        elif 'shove' in trick_name_lower or 'shov' in trick_name_lower or 'spin' in trick_name_lower or '360' in trick_name_lower or '180' in trick_name_lower or 'rotation' in trick_name_lower:
            return "Shove-Its & Spins"
        elif 'ollie' in trick_name_lower:
            return "Ollie-Based Tricks"
        else:
            return "Other"

    # Create a section for each category
    categories = [
        "Beginner",
        "Easy",
        "Intermediate",
        "Advanced",
        "Expert"
    ]

    # Display buttons for each category
    for category in categories:
        st.subheader(category)
        st.text("")

        # Get tricks for this category
        category_tricks = df_tricks[df_tricks['Category'] == category]

        # Apply trick type filter if not "All Tricks"
        if trick_type != "All Tricks":
            # Filter based on trick type
            filtered_tricks = []
            for _, trick in category_tricks.iterrows():
                if get_trick_type(trick['Trick']) == trick_type:
                    filtered_tricks.append(trick)

            # Convert filtered list back to DataFrame
            if filtered_tricks:
                category_tricks = pd.DataFrame(filtered_tricks)
            else:
                category_tricks = pd.DataFrame(columns=category_tricks.columns)

        # Skip empty categories after filtering
        if len(category_tricks) == 0:
            st.info(f"No {trick_type} tricks found in {category} category.")
            continue


        # Create columns for the buttons
        columns_per_row = 4

        # Calculate how many rows we need
        num_tricks = len(category_tricks)
        num_rows = (num_tricks + columns_per_row - 1) // columns_per_row

        # Create buttons in rows
        for row in range(num_rows):
            cols = st.columns(columns_per_row)

            # Add buttons to each column
            for col_idx in range(columns_per_row):
                trick_idx = row * columns_per_row + col_idx

                # Check if we have a trick for this position
                if trick_idx < num_tricks:
                    trick = category_tricks.iloc[trick_idx]

                    # Check if this trick is completed
                    is_completed = trick['Trick'] in completed_tricks['completed']

                    # Create a centered container for the button
                    with cols[col_idx]:
                        # Create button with trick name and green checkmark if completed
                        button_text = f"{trick['Trick']}"
                        if is_completed:
                            button_text = f"{trick['Trick']} ✅"

                        if st.button(
                                button_text,
                                key=f"{trick['Trick']}_{trick['Difficulty']}",
                                use_container_width=True,
                                on_click=store_trick_selection,
                                args=(trick['Trick'], trick['Difficulty'])
                        ):
                            pass  # The callback handles the navigation

    # Add a separator between categories
    st.markdown("---")


# Run the main function
if __name__ == "__main__":
    main()

if 'redirect_to_page' in st.session_state and st.session_state.redirect_to_page:
    page = st.session_state.redirect_to_page
    st.session_state.redirect_to_page = None  # Clear to prevent infinite loop
    st.switch_page(page)