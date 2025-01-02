import requests
import json
import os
import time
from Forum.Reddit import Reddit
from Forum.Leetcode import Leetcode
from dotenv import load_dotenv
from LLM.Gemini import Gemini
from LLM.ChatGPT import ChatGPT

# Load environment variables from .env file
load_dotenv()

REDDIT_ACCESS_TOKEN = os.environ.get("REDDIT_ACCESS_TOKEN")
GEMINI_ACCESS_TOKEN = os.environ["GEMINI_API_KEY"]
CHATGPT_ACCESS_TOKEN = os.environ["CHATGPT_API_KEY"]

if not REDDIT_ACCESS_TOKEN:
    raise EnvironmentError("REDDIT_ACCESS_TOKEN is not set in the environment variables.")

if not GEMINI_ACCESS_TOKEN:
    raise EnvironmentError("GEMINI_ACCESS_TOKEN is not set in the environment variables.")

if not CHATGPT_ACCESS_TOKEN:
    raise EnvironmentError("GEMINI_ACCESS_TOKEN is not set in the environment variables.")

# Create Forums
reddit_forum = Reddit(REDDIT_ACCESS_TOKEN)
leetcode_forum = Leetcode()

# Choose the forum
forum = reddit_forum

#Select the llm
#gemini = Gemini(GEMINI_ACCESS_TOKEN)
chatgpt = ChatGPT(CHATGPT_ACCESS_TOKEN)  # Ensure you have the correct API key in your .env
llm = chatgpt

# Define the range of pages to fetch
start_page, end_page = 1, 5

# Fetch posts from the forum
posts = forum.fetch_posts(filter_keyword="amazon", start_page=start_page, end_page=end_page)

keywords_to_filter_out = [" oa ", " online assessment ", " oa","|oa","|online assessment", " online assessment"]
# Function to filter out posts that mention online assessment
def filter_posts(posts, keywords):
    filtered_posts = []
    
    for post in posts:
        title = post['title'].lower()  # Convert title to lowercase for case-insensitive matching
        if not any(keyword in title for keyword in keywords):
            filtered_posts.append(post)
    
    return filtered_posts

# Filter the posts
filtered_posts = filter_posts(posts, keywords_to_filter_out)

prompt = (
    "Does this post have an amazon coding onsite question or amazon leadership principle question where the exact question has been mentioned in the post?"
    "Answer with only either oq(onsite question) or lp(leadership principle question) or both if it has such a question and the exact question has been described else response should be no"
)

# Initialize list to store URLs with 'yes' response
urls_with_yes = []

# Get the filename dynamically using the LLM
file_name = llm.get_response("Suggest only one name for a file containing URLs that match this criteria: " + prompt)
file_name = file_name.strip().replace(" ", "_")

# Generate the file path
file_path = os.path.join(os.getcwd(), file_name)

# Open the file for writing
with open(file_path, "w", encoding="utf-8") as file:

    # Loop through the posts
    for post in posts:
        post_id = post.get("postid")
        post_url = post.get("url")

        # Fetch conversation for the post
        conversation = forum.fetch_conversation(post_id)
        
        if conversation:
            # Use the LLM to analyze the conversation
            response = llm.get_response(conversation + "\n" + prompt)
            
            # If the response is "yes", append the URL to the list and write it to the file
            if response and response.strip().lower() != "no":
                urls_with_yes.append(post_url)
                file.write(post_url +" " +response.strip().lower() + "\n")
                print(post_url)

        # Introduce a sleep time to ensure we don't exceed the rate limit (2,000 RPM)
        time.sleep(60 / 1000)  # Sleep for 0.03 seconds between requests to stay within 2000 RPM limit

# Print the name of the file where URLs were saved
print(f"URLs saved to file: {file_name}_{start_page}_{end_page}")
