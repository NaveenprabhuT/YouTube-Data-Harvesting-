import streamlit as st
import pandas as pd
from googleapiclient.discovery import build

st.image("G:\DATA SCIENCE/yt.jpg", caption='Youtube Data', use_column_width=True)

# Custom CSS for the app
custom_css = """
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #5a5ab6;
    color: #212b35;
}
.stButton>button {
    background-color: #212b35;
    color: Yellow;
}
</style>
"""

# Apply custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Function to fetch data from YouTube API
def fetch_youtube_data(api_key, channel_id):
    # Initialize the YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Call the API to retrieve channel data
    response = youtube.channels().list(
        part='snippet, statistics',
        id=channel_id
    ).execute()

    # Extract relevant data from the API response
    channel_info = response['items'][0]['snippet']
    statistics = response['items'][0]['statistics']

    # Return the extracted data
    return {
        'Channel Name': channel_info['title'],
        'Subscribers': statistics.get('subscriberCount', 0),
        'Total Videos': statistics.get('videoCount', 0),
        'Total Views': statistics.get('viewCount', 0),
        'Playlist ID': channel_info.get('playlistId', ''),
        'Channel Description': channel_info.get('description', '')
    }

# Streamlit app layout
st.title("YouTube Data Fetcher")

# Input fields for API key and channel ID
api_key = ("AIzaSyBctX0lxhmYWNlTZEXHxkgPxc8TfWSo9yw")
channel_id = st.text_input("Enter YouTube Channel ID:")

# Button to fetch data
if st.button("Fetch Data"):
    if api_key and channel_id:
        # Fetch data from YouTube API
        try:
            data = fetch_youtube_data(api_key, channel_id)
            # Display the fetched data
            st.write(data)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter channel ID.")

