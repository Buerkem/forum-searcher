import requests
import json
import os
from Forum import Forum
from apply_prompt_to_text import apply_prompt_to_text
from Reddit import Reddit
from Leetcode import Leetcode
from dotenv import load_dotenv

load_dotenv()

prompt = "does this post have comments? answer with either yes or no."

REDDIT_ACCESS_TOKEN = os.environ.get("REDDIT_ACCESS_TOKEN")
if not REDDIT_ACCESS_TOKEN:
    print("Error: REDDIT_ACCESS_TOKEN is not set in the environment variables.")
    exit(1)

reddit_forum = Reddit(REDDIT_ACCESS_TOKEN)
leetcode_forum = Leetcode()

forum = leetcode_forum

start_page, end_page = 1, 2
posts = forum.fetch_posts(start_page=start_page, end_page=end_page)

for post in posts:
    post_id = post.get("postid")
    post_url = post.get("url")

    print(f"Post URL: {post_url}")

    conversation = forum.fetch_conversation(post_id)
    if conversation:
        print(f"Conversation: {conversation}")

        response = apply_prompt_to_text(conversation, prompt)

        if response.strip().lower() == "yes":
            print(json.dumps(post, ensure_ascii=False, indent=4))
    else:
        print(f"Error: No conversation found for post ID {post_id}.")
