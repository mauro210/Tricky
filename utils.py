import streamlit as st
import pandas as pd
import json
import os
import re


# Function to extract YouTube video ID from URL
def extract_youtube_id(url):
    """Extract the YouTube video ID from a URL"""
    # Patterns for YouTube URLs
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\?/]+)',  # Standard and short URLs
        r'youtube\.com/embed/([^/\?]+)'  # Embed URLs
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # If no match found, return the original URL (might be a direct video ID)
    if '/' not in url and '?' not in url and len(url) < 20:
        return url

    return None


# Create a function to load or create the tricks database
@st.cache_data
def load_tricks_data():
    """Load the skateboarding tricks data from CSV file"""
    try:
        df = pd.read_csv('skateboard_tricks.csv')
        return df
    except FileNotFoundError:
        # If file doesn't exist, create it
        return create_default_data()


def create_default_data():
    """Create default data if CSV doesn't exist"""
    # Create a list of (trick, difficulty) pairs
    tricks_data = [
        ("Tic-Tac", 1),
        ("Kickturn", 2),
        ("Powerslide", 5),
        ("Ollie", 10),
        # Include other tricks here
        ("720 Flip", 90)
    ]

    # Create DataFrame from the list of tuples
    df = pd.DataFrame(tricks_data, columns=["Trick", "Difficulty"])

    # Save to CSV
    df.to_csv('skateboard_tricks.csv', index=False)

    return df


# Define difficulty categories
def get_difficulty_category(difficulty):
    if difficulty <= 10:
        return "Beginner"
    elif difficulty <= 30:
        return "Easy"
    elif difficulty <= 50:
        return "Intermediate"
    elif difficulty <= 70:
        return "Advanced"
    else:
        return "Expert"


# Function to create and save video data JSON if it doesn't exist
def initialize_video_data():
    # Check if the video data file exists
    if not os.path.exists('trick_videos.json'):
        # Create a template for the video data
        video_data = {}

        # Load the tricks from CSV
        tricks_df = load_tricks_data()

        # Create an entry for each trick with placeholder video URLs
        for _, row in tricks_df.iterrows():
            trick_name = row['Trick']
            video_data[trick_name] = {
                "slow_motion": {
                    "url": "",
                    "start_time": None,
                    "end_time": None
                },
                "pro_examples": [],  # List of pro examples with time controls
                "tutorial": ""  # Single tutorial video URL
            }

        # Save the video data to a JSON file
        with open('trick_videos.json', 'w') as f:
            json.dump(video_data, f, indent=4)

        return video_data
    else:
        # Load existing video data
        with open('trick_videos.json', 'r') as f:
            return json.load(f)


# Function to load or create the tricks completion data
def load_completed_tricks():
    """Load the completed tricks data from JSON file"""
    if not os.path.exists('completed_tricks.json'):
        # Create an empty completed tricks list
        completed_tricks = {
            "completed": []
        }

        # Save to JSON
        with open('completed_tricks.json', 'w') as f:
            json.dump(completed_tricks, f, indent=4)

        return completed_tricks
    else:
        # Load existing completed tricks
        with open('completed_tricks.json', 'r') as f:
            return json.load(f)


# Function to save completed tricks
def save_completed_tricks(completed_tricks):
    """Save the completed tricks data to JSON file"""
    with open('completed_tricks.json', 'w') as f:
        json.dump(completed_tricks, f, indent=4)


# Function to replay video by incrementing counter
def replay_video(video_key):
    """Increment video counter to force iframe refresh"""
    if video_key not in st.session_state.video_replay_counters:
        st.session_state.video_replay_counters[video_key] = 0

    # Increment counter to force iframe refresh
    st.session_state.video_replay_counters[video_key] += 1

    # Set only this specific video's replay flag to true
    st.session_state.active_replays[video_key] = True


# Function to display YouTube video with replay button
def display_video_with_replay(url, start_time=None, end_time=None, button_text="↻ Replay", video_key=None, height=450):
    # Extract video ID
    video_id = extract_youtube_id(url)
    if not video_id:
        st.error(f"Could not extract YouTube video ID from: {url}")
        return

    # Make sure video_key exists
    if video_key is None:
        video_key = f"video_{video_id}"

    # Make sure counter exists
    if video_key not in st.session_state.video_replay_counters:
        st.session_state.video_replay_counters[video_key] = 0

    # Build URL with parameters
    video_params = []
    if start_time is not None:
        video_params.append(f"start={start_time}")
    if end_time is not None:
        video_params.append(f"end={end_time}")

    # Add cache busting parameter to force reload
    video_params.append(f"nocache={st.session_state.video_replay_counters[video_key]}")

    # Add autoplay if this specific video is being actively replayed
    if video_key in st.session_state.active_replays and st.session_state.active_replays[video_key]:
        video_params.append("autoplay=1")
        # Reset the flag after using it once
        st.session_state.active_replays[video_key] = False

    # Hide related videos and use modest branding
    video_params.append("rel=0&modestbranding=1")

    # Construct final URL
    video_url = f"https://www.youtube.com/embed/{video_id}?{'&'.join(video_params)}"

    # Display the video using iframe with proper aspect ratio
    st.markdown(
        f'''
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin-bottom: 10px;">
          <iframe 
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
            height="{height}" 
            src="{video_url}" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
          </iframe>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    # Add replay button with on_click handler
    if st.button(button_text, key=f"btn_{video_key}", on_click=replay_video, args=(video_key,)):
        pass  # The on_click handler takes care of the action


# Initialize session state variables needed across pages
def initialize_session_state():
    """Initialize all the session state variables needed for the application"""
    # Video replay counters
    if 'video_replay_counters' not in st.session_state:
        st.session_state.video_replay_counters = {}

    # Active replays tracking
    if 'active_replays' not in st.session_state:
        st.session_state.active_replays = {}

    # Selected trick information (for the trick detail page)
    if 'selected_trick' not in st.session_state:
        st.session_state.selected_trick = None

    if 'selected_difficulty' not in st.session_state:
        st.session_state.selected_difficulty = None


# NEW: Function to get global data, loading it only once
@st.cache_resource
def get_global_data():
    """Load and initialize all global data, ensuring it's only loaded once"""
    # Load tricks data and add category
    df = load_tricks_data()
    df['Category'] = df['Difficulty'].apply(get_difficulty_category)

    # Load video data
    videos = initialize_video_data()

    # Load completed tricks
    completed = load_completed_tricks()

    # Return everything as a dictionary
    return {
        "df_tricks": df,
        "video_data": videos,
        "completed_tricks": completed
    }


# Function to access global data
def get_tricks_df():
    """Get the tricks dataframe"""
    return get_global_data()["df_tricks"]


def get_video_data():
    """Get the video data"""
    return get_global_data()["video_data"]


def get_completed_tricks():
    """Get the completed tricks data"""
    return get_global_data()["completed_tricks"]