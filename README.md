**YouTube Data Harvesting and Warehousing**

**Overview:**
This project aims to develop a user-friendly Streamlit application that utilizes the Google API to extract information on YouTube channels, stores it in a SQL database, and enables users to search for channel details and join tables to view data in the Streamlit app.

**Features:**
Input a YouTube channel ID and retrieve all relevant data (channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, comments of each video) using the Google API.
Collect data for up to 10 different YouTube channels and store them in a SQL data warehouse.
Option to store the data in MySQL or PostgreSQL.
Search and retrieve data from the SQL database using different search options, including joining tables to get channel details.

**Setup:**
Clone this repository to your local machine.
Install the required dependencies by running "pip install streamlit.txt.
Obtain a YouTube Data API key from the Google Cloud Console.
Set up a SQL database (MySQL or PostgreSQL) and configure the connection details in the Streamlit app.
Run the Streamlit app using the command "streamlit run file.py".
Enter your YouTube API key and channel ID to retrieve and analyze YouTube data.

**Project Structure:**
'app.py': Main Streamlit application code.   
'requirements.txt': List of Python dependencies.    
'README.md': Project documentation.   

**Usage:**
Input your YouTube API key and channel ID in the provided fields.
Click the "Fetch Data" button to retrieve channel information from the YouTube API.
View and analyze the fetched data in the Streamlit app.
Use the search and filtering options to query the SQL database and explore channel details.

**Next Steps:**
Enhance the user interface with improved styling and layout.
Implement additional features such as data visualization and trend analysis.
Optimize database queries and data retrieval for better performance.
Conduct thorough testing and debugging to ensure application stability and reliability.
Document any additional features or updates in the README file.
