import requests
import json
import os
from Forum.Reddit import Reddit
from Forum.Leetcode import Leetcode
from dotenv import load_dotenv
from LLM.Gemini import Gemini

# Load environment variables from .env file
load_dotenv()

# Define the prompt to be used
prompt = "does this post have comments? answer with either yes or no."

# Ensure the Reddit API access token is available
REDDIT_ACCESS_TOKEN = os.environ.get("REDDIT_ACCESS_TOKEN")
if not REDDIT_ACCESS_TOKEN:
    print("Error: REDDIT_ACCESS_TOKEN is not set in the environment variables.")
    exit(1)

# Create instances of the respective classes
reddit_forum = Reddit(REDDIT_ACCESS_TOKEN)
leetcode_forum = Leetcode()

# Here, select which forum to use, for example, we use leetcode_forum
forum = leetcode_forum

# Initialize the Gemini LLM with your API key
print(os.environ["GEMINI_API_KEY"],"xxx")
llm = Gemini(os.environ["GEMINI_API_KEY"]) 

# Fetch posts from the forum
start_page, end_page = 1, 2
posts = forum.fetch_posts(start_page=start_page, end_page=end_page)

# Loop through the posts and process each one
for post in posts:
    post_id = post.get("postid")
    post_url = post.get("url")

    print(f"Post URL: {post_url}")

    # Fetch conversation (comments or discussion) for the post
    conversation = forum.fetch_conversation(post_id)
    if conversation:
        print(f"Conversation: {conversation}")

        # Get response from Gemini LLM
        response = llm.get_response(conversation + "\n" + prompt)

        # Check if the response is "yes" or "no" (case insensitive)
        if response and response.strip().lower() == "yes":
            print(json.dumps(post, ensure_ascii=False, indent=4))
    else:
        print(f"Error: No conversation found for post ID {post_id}.")