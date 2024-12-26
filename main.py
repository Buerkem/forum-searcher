import requests
import json
import os
from Forum.Reddit import Reddit
from Forum.Leetcode import Leetcode
from dotenv import load_dotenv
from LLM.Gemini import Gemini

# Load environment variables from .env file
load_dotenv()

REDDIT_ACCESS_TOKEN = os.environ.get("REDDIT_ACCESS_TOKEN")
if not REDDIT_ACCESS_TOKEN:
    raise EnvironmentError("REDDIT_ACCESS_TOKEN is not set in the environment variables.")

GEMINI_ACCESS_TOKEN = os.environ["GEMINI_API_KEY"]
if not REDDIT_ACCESS_TOKEN:
    raise EnvironmentError("GEMINI_ACCESS_TOKEN is not set in the environment variables.")


# Create Forums
reddit_forum = Reddit(REDDIT_ACCESS_TOKEN)
leetcode_forum = Leetcode()

# Choose the forum
forum = leetcode_forum

# Initialize the Gemini LLM
llm = Gemini(GEMINI_ACCESS_TOKEN)

# Define the range of pages to fetch
start_page, end_page = 1, 200

# Fetch posts from the forum
posts = forum.fetch_posts(filter_keyword="amazon", start_page=start_page, end_page=end_page)
prompt = (
    "Does this post have a system design or object oriented design question or low level design question? "
    "Answer with either yes or no if probability of the question matching the criteria is greater than 0.6"
)

urls_with_yes = []

for post in posts:
    post_id = post.get("postid")
    post_url = post.get("url")

    # Fetch conversation for the post
    conversation = forum.fetch_conversation(post_id)
    if conversation:
        # Use the LLM to analyze the conversation
        response = llm.get_response(conversation + "\n" + prompt)
        
        # If the response is "yes", add the URL to the list
        if response and response.strip().lower() == "yes":
            urls_with_yes.append(post_url)
            print(post_url)

# Use LLM to name the file dynamically
file_name = llm.get_response("Suggest a name for a file containing urls that match this criteria: "+prompt)

# Format the file name properly
file_name = file_name.strip().replace(" ", "_")
file_path = os.path.join(os.getcwd(), file_name)

# Write the URLs to the file
with open(file_path, "w", encoding="utf-8") as file:
    for url in urls_with_yes:
        file.write(url + "\n")

# Print the name of the file where URLs were saved
print(f"URLs saved to file: {file_name}")
