import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import from the main file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the main file
from utils import (
    display_video_with_replay,
    get_tricks_df, get_video_data, get_completed_tricks, save_completed_tricks
)

df_tricks = get_tricks_df()
video_data = get_video_data()
completed_tricks = get_completed_tricks()

# Set page config
st.set_page_config(page_title="Trick Page", layout="wide", initial_sidebar_state="collapsed")

# Callback function for navigation to similar tricks
def navigate_to_similar_trick(trick_name, difficulty):
    st.session_state.selected_trick = trick_name
    st.session_state.selected_difficulty = difficulty
    st.session_state.redirect_to_page = "pages/Trick_Page.py"

# Check if we have the required session state
if 'selected_trick' not in st.session_state or st.session_state.selected_trick is None:
    st.error("No trick selected. Please go back to the home page and select a trick.")
    if st.button("Go to Home Page"):
        st.switch_page("Home.py")
else:

    trick_name = st.session_state.selected_trick
    difficulty = st.session_state.selected_difficulty

    # Add back button
    if st.button(":material/arrow_back: All Tricks 🛹"):
        st.switch_page("Home.py")

    # Center the trick name and difficulty
    st.markdown(f"<h1 style='text-align: center;'>{trick_name}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Difficulty: {difficulty}/100</h3>", unsafe_allow_html=True)

    # Get the videos for this trick
    trick_videos = video_data.get(trick_name, {
        "slow_motion": {"url": "", "start_time": None, "end_time": None},
        "pro_examples": [],
        "tutorial": ""
    })

    # Display slow motion video if available
    st.subheader("Slow Motion Demonstration")
    if trick_videos["slow_motion"]["url"]:
        # Create a unique key for the slow motion video
        slow_mo_key = f"slow_mo_{trick_name}"

        # Display video with replay button
        display_video_with_replay(
            trick_videos["slow_motion"]["url"],
            start_time=trick_videos["slow_motion"]["start_time"],
            end_time=trick_videos["slow_motion"]["end_time"],
            button_text="↻ Replay",
            video_key=slow_mo_key,
            height=450
        )
    else:
        st.info(f"No slow motion video available for {trick_name} yet. Check back later!")

    # Display pro examples if available
    st.subheader("Pro Skater Examples")
    if trick_videos["pro_examples"]:
        pro_cols = st.columns(min(3, len(trick_videos["pro_examples"])))
        for i, example in enumerate(trick_videos["pro_examples"]):
            with pro_cols[i % 3]:
                st.markdown(f"**{example['name']}**")

                # Create a unique key for this pro example
                pro_key = f"pro_{trick_name}_{i}"

                # Display video with replay button
                display_video_with_replay(
                    example["url"],
                    start_time=example["start_time"],
                    end_time=example["end_time"],
                    button_text="↻ Replay",
                    video_key=pro_key,
                    height=350
                )
    else:
        st.info(f"No pro examples available for {trick_name} yet. Check back later!")

    # Display a tutorial video if available
    st.subheader("Tutorial Video")
    if trick_videos["tutorial"]:
        st.video(trick_videos["tutorial"])
    else:
        st.info(f"No tutorial video available for {trick_name} yet. Check back later!")

    # Add the "Mark as Learned" section at the bottom before similar tricks
    st.markdown("---")

    # Create a centered container for the completion checkbox
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown("<h3 style='text-align: center;'>Mark as Learned</h3>", unsafe_allow_html=True)

        # Center the checkbox using columns
        _, checkbox_col, _ = st.columns([3, 2, 3])
        with checkbox_col:
            # Initialize the checkbox state in session state if not already present
            checkbox_key = f"completed_{trick_name}"
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = trick_name in completed_tricks['completed']

            # Create a callback function to handle checkbox changes
            def on_checkbox_change():
                # Update the completed_tricks list based on the new checkbox state
                if st.session_state[checkbox_key]:
                    if trick_name not in completed_tricks['completed']:
                        completed_tricks['completed'].append(trick_name)
                else:
                    if trick_name in completed_tricks['completed']:
                        completed_tricks['completed'].remove(trick_name)

                # Save updated completed tricks
                save_completed_tricks(completed_tricks)

            # Display the checkbox with the callback
            st.checkbox(
                "I can do this trick!",
                key=checkbox_key,
                on_change=on_checkbox_change
            )

    st.markdown("---")

    # Display similar tricks
    st.subheader("Similar Tricks You Might Like")
    # Find tricks with similar difficulty (within ±10)
    similar_tricks_df = df_tricks[
        (df_tricks["Difficulty"] >= difficulty - 10) &
        (df_tricks["Difficulty"] <= difficulty + 10) &
        (df_tricks["Trick"] != trick_name)
        ]

    # Check if we have any similar tricks
    if len(similar_tricks_df) > 0:
        # Get a sample of up to 5 similar tricks
        sample_size = min(5, len(similar_tricks_df))

        # Use a consistent seed for sampling to prevent random changes on button clicks
        similar_tricks = similar_tricks_df.sample(sample_size, random_state=42)

        similar_cols = st.columns(sample_size)
        for i, (_, similar_trick) in enumerate(similar_tricks.iterrows()):
            with similar_cols[i]:
                # Check if this similar trick is completed
                is_completed = similar_trick['Trick'] in completed_tricks['completed']

                # Create button for the similar trick with checkmark if completed
                button_text = f"{similar_trick['Trick']}"
                if is_completed:
                    button_text = f"{similar_trick['Trick']} ✅"

                if st.button(
                        button_text,
                        key=f"similar_{similar_trick['Trick']}_{i}",
                        use_container_width=True,
                        on_click=navigate_to_similar_trick,
                        args=(similar_trick['Trick'], similar_trick['Difficulty'])
                ):
                    pass  # The callback handles the navigation
    else:
        st.info("No similar tricks found with comparable difficulty levels.")

if 'redirect_to_page' in st.session_state and st.session_state.redirect_to_page:
    page = st.session_state.redirect_to_page
    st.session_state.redirect_to_page = None
    st.switch_page(page)