# Importing the necessary libraries
import pandas as pd
import plotly.express as px
import streamlit as st
import mysql.connector as sql
import pymongo
from googleapiclient.discovery import build
from PIL import Image

# SETTING PAGE CONFIGURATIONS
icon = Image.open("G:/DATA SCIENCE/Ytube.png")
st.set_page_config(
    page_title="Youtube Data Harvesting and Warehousing | By Naveen T",
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': """# This app is created by *Naveen T*"""})

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(host="localhost",
                   user="root",
                   password="",
                   database="youtube")
mycursor = mydb.cursor(buffered=True)


# FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(channel_id):
    ch_data = []
    response = youtube.channels().list(part='snippet,contentDetails,statistics',
                                       id=channel_id).execute()

    for item in response['items']:
        data = {
            "Channel_id": item['id'],
            "Channel_name": item['snippet']['title'],
            "Playlist_id": item['contentDetails']['relatedPlaylists']['uploads'],
            "Subscribers": item['statistics']['subscriberCount'],
            "Views": item['statistics']['viewCount'],
            "Total_videos": item['statistics']['videoCount'],
            "Description": item['snippet']['description'],
            "Country": item['snippet'].get('country')
        }
        ch_data.append(data)
    return ch_data


# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id, part='snippet', maxResults=50, pageToken=next_page_token).execute()
        
        for item in res['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if not next_page_token:
            break
    return video_ids


# FUNCTION TO GET VIDEO DETAILS
def get_video_details(v_ids):
    video_stats = []
    for i in range(0, len(v_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(v_ids[i:i+50])).execute()
        for video in response['items']:
            video_details = {
                "Channel_name": video['snippet']['channelTitle'],
                "Channel_id": video['snippet']['channelId'],
                "Video_id": video['id'],
                "Title": video['snippet']['title'],
                "Tags": video['snippet'].get('tags'),
                "Thumbnail": video['snippet']['thumbnails']['default']['url'],
                "Description": video['snippet']['description'],
                "Published_date": video['snippet']['publishedAt'],
                "Duration": video['contentDetails']['duration'],
                "Views": video['statistics']['viewCount'],
                "Likes": video['statistics'].get('likeCount'),
                "Comments": video['statistics'].get('commentCount'),
                "Favorite_count": video['statistics']['favoriteCount'],
                "Definition": video['contentDetails']['definition'],
                "Caption_status": video['contentDetails']['caption']
            }
            video_stats.append(video_details)
    return video_stats


# FUNCTION TO GET COMMENT DETAILS
def get_comments_details(v_id):
    comment_data = []
    try:
        next_page_token = None
        while True:
            response = youtube.commentThreads().list(part="snippet,replies",
                                                      videoId=v_id,
                                                      maxResults=100,
                                                      pageToken=next_page_token).execute()
            for cmt in response['items']:
                data = {
                    "Comment_id": cmt['id'],
                    "Video_id": cmt['snippet']['videoId'],
                    "Comment_text": cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                    "Comment_author": cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    "Comment_posted_date": cmt['snippet']['topLevelComment']['snippet']['publishedAt'],
                    "Like_count": cmt['snippet']['topLevelComment']['snippet']['likeCount'],
                    "Reply_count": cmt['snippet']['totalReplyCount']
                }
                comment_data.append(data)
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
    except Exception as e:
        print(e)
    return comment_data


# FUNCTION TO GET CHANNEL NAMES FROM MONGODB
def channel_names():
    ch_name = []
    for i in db.channel_details.find():
        ch_name.append(i['Channel_name'])
    return ch_name


# BRIDGING A CONNECTION WITH MONGODB ATLAS AND CREATING A NEW DATABASE(YOUTUBE_DATA)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['youtubedata']

# BUILDING CONNECTION WITH YOUTUBE API
api_key = "AIzaSyBctX0lxhmYWNlTZEXHxkgPxc8TfWSo9yw"
youtube = build('youtube', 'v3', developerKey=api_key)

# Assuming you have navigation links in a Streamlit sidebar
selected = st.sidebar.radio("Navigation", ["Home", "Extract and Transform", "View"])

# HOME PAGE
if selected == "Home":
    
    col1, col2 = st.columns(2)
    col1.markdown("## :blue[Domain] : Social Media")
    col1.markdown("## :blue[Technologies used] : Python,MongoDB, Youtube Data API, MySql, Streamlit")
    col1.markdown("## :blue[Overview] : Retrieving the Youtube channels data from the Google API, storing it in a MongoDB as data lake, migrating and transforming data into a SQL database,then querying the data and displaying it in the Streamlit app.")
    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.image("youtube.png")

# EXTRACT and TRANSFORM PAGE
if selected == "Extract and Transform":
    tab1, tab2 = st.tabs(["$\huge EXTRACT $", "$\huge TRANSFORM $"])
    # EXTRACT TAB
    with tab1:
        st.markdown("#    ")
        st.write("### Enter YouTube Channel_ID below :")
        ch_id = st.text_input("Hint : Goto channel's home page > Right click > View page source > Find channel_id").split(',')

        if ch_id and st.button("Extract Data"):
            ch_details = get_channel_details(ch_id)
            st.write(f'#### Extracted data from :green["{ch_details[0]["Channel_name"]}"] channel')
            st.table(ch_details)

        if st.button("Upload to MongoDB"):
            with st.spinner('Please Wait for it...'):
                ch_details = get_channel_details(ch_id)
                v_ids = get_channel_videos(ch_id)
                vid_details = get_video_details(v_ids)
                
                def comments():
                    com_d = []
                    for i in v_ids:
                        com_d += get_comments_details(i)
                    return com_d
                
                comm_details = comments()

                collections1 = db.channel_details
                collections1.insert_many(ch_details)

                collections2 = db.video_details
                collections2.insert_many(vid_details)

                collections3 = db.comments_details
                collections3.insert_many(comm_details)
                st.success("Upload to MogoDB successful !!")
      
    # TRANSFORM TAB
    with tab2:     
        st.markdown("#   ")
        st.markdown("### Select a channel to begin Transformation to SQL")
        
        ch_names = channel_names()
        user_inp = st.selectbox("Select channel", options=ch_names)
        
        def insert_into_channels():
            collections = db.channel_details
            query = """INSERT INTO channels VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""
                
            for i in collections.find({"Channel_name": user_inp}, {'_id': 0}):
                mycursor.execute(query, tuple(i.values()))
                mydb.commit()
                
        def insert_into_videos():
            collectionss = db.video_details
            query1 = """INSERT INTO videos VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

            for i in collectionss.find({"Channel_name": user_inp}, {"_id": 0}):
                t = tuple(i.values())
                mycursor.execute(query1, t)
                mydb.commit()

        def insert_into_comments():
            collections1 = db.video_details
            collections2 = db.comments_details
            query2 = """INSERT INTO comments VALUES(%s,%s,%s,%s,%s,%s,%s)"""

            for vid in collections1.find({"Channel_name": user_inp}, {'_id': 0}):
                for i in collections2.find({'Video_id': vid['Video_id']}, {'_id': 0}):
                    t = tuple(i.values())
                    mycursor.execute(query2, t)
                    mydb.commit()

        if st.button("Submit"):
            try:
                insert_into_channels()
                insert_into_videos()
                insert_into_comments()
                st.success("Transformation to MySQL Successful!!!")
            except:
                st.error("Channel details already transformed!!")

# VIEW PAGE
if selected == "View":
    
    st.write("## :orange[Select any question to get Insights]")
    questions = st.selectbox('Questions', [
        'Click the question that you would like to query',
        '1. What are the names of all the videos and their corresponding channels?',
        '2. Which channels have the most number of videos, and how many videos do they have?',
        '3. What are the top 10 most viewed videos and their respective channels?',
        '4. How many comments were made on each video, and what are their corresponding video names?',
        '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
        '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
        '7. What is the total number of views for each channel, and what are their corresponding channel names?',
        '8. What are the names of all the channels that have published videos in the year 2022?',
        '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
        '10. Which videos have the highest number of comments, and what are their corresponding channel names?'
    ])
    
    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute("""SELECT title AS Video_Title, channel_name AS Channel_Name FROM videos ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        
    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, total_videos AS Total_Videos
                            FROM channels
                            ORDER BY total_videos DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Number of videos in each channel :]")
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig, use_container_width=True)
        
    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, title AS Video_Title, views AS Views 
                            FROM videos
                            ORDER BY views DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most viewed videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig, use_container_width=True)
        
    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT a.video_id AS Video_id, a.title AS Video_Title, b.Total_Comments
                            FROM videos AS a
                            LEFT JOIN (SELECT video_id,COUNT(comment_id) AS Total_Comments
                            FROM comments GROUP BY video_id) AS b
                            ON a.video_id = b.video_id
                            ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
          
    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, title AS Title, likes AS Likes_Count 
                            FROM videos
                            ORDER BY likes DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most liked videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT title AS Video_Title, SUM(likes) AS Total_Likes, SUM(dislikes) AS Total_Dislikes 
                            FROM videos 
                            GROUP BY title""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, SUM(views) AS Total_Views 
                            FROM videos 
                            GROUP BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        mycursor.execute("""SELECT DISTINCT channel_name AS Channel_Name 
                            FROM videos 
                            WHERE YEAR(published_date) = 2022""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, AVG(duration) AS Avg_Duration 
                            FROM videos 
                            GROUP BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mycursor.execute("""SELECT a.channel_name AS Channel_Name, a.title AS Video_Title, b.Total_Comments 
                            FROM videos AS a 
                            LEFT JOIN (SELECT video_id, COUNT(comment_id) AS Total_Comments 
                                        FROM comments 
                                        GROUP BY video_id) AS b 
                            ON a.video_id = b.video_id 
                            ORDER BY b.Total_Comments DESC 
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
