from Forum.Forum import Forum
import requests
import os

class Reddit(Forum):
    API_BASE_URL = "https://oauth.reddit.com"
    SUBREDDIT_BASE_URL = f"{API_BASE_URL}/r/leetcode"
    COMMENTS_URL_TEMPLATE = f"{SUBREDDIT_BASE_URL}/comments/{{postid}}/"

    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "RedditAPI/0.1 by YourUsername"
        }

    def fetch_posts(self, filter_keyword: str = "", start_page: int = 1, end_page: int = 2):
        """
        Fetch posts from Reddit discussions between start and end pages.
        Filters posts by the provided keyword if specified.
        Returns a list of dictionaries containing post details (title, post URL, and ID).
        
        Args:
            filter_keyword (str): Keyword to filter posts by title (case-insensitive).
            start_page (int): The starting page number for fetching posts.
            end_page (int): The ending page number for fetching posts.
        """
        posts_per_page = 100  # Number of posts to fetch per page
        after = None
        posts = []
        posts_url = f"{self.SUBREDDIT_BASE_URL}/new"

        for page in range(start_page, end_page + 1):
            params = {"limit": posts_per_page}
            if after:
                params["after"] = after

            response = requests.get(posts_url, headers=self.headers, params=params)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch posts: {response.status_code} {response.text}")

            data = response.json()
            filtered_posts = [
                {"title": post["data"]["title"], "url": f"https://reddit.com{post['data']['permalink']}", "postid": post["data"]["id"]}
                for post in data["data"]["children"]
                if filter_keyword.lower() in post["data"]["title"].lower()  # Check if keyword is in the title
            ]
            posts.extend(filtered_posts)

            after = data["data"]["after"]
            if not after:
                break  # End of pages

        return posts

    def fetch_conversation(self, postid: str, max_comments: int = 50, max_nesting: int = 6):
        """
        Fetches the conversation for a specific LeetCode discussion.
        Returns the conversation as a string representation.
        """
        def extract_comments(comments_list, depth=0):
            if depth > max_nesting:
                return []

            extracted = []
            for comment in comments_list[:max_comments]:
                if comment['kind'] == 't1':  # Ensure it's a comment
                    data = comment['data']
                    comment_obj = {
                        "author": data.get('author', '[deleted]'),
                        "body": data.get('body', ''),
                        "replies": []  # Placeholder for nested comments
                    }

                    # Check if there are replies and recurse
                    replies = data.get('replies')
                    if isinstance(replies, dict):  # Ensure replies is a dictionary
                        nested_comments = replies.get('data', {}).get('children', [])
                        comment_obj["replies"] = extract_comments(nested_comments, depth + 1)

                    extracted.append(comment_obj)
            return extracted

        def format_comments(comments, depth=0):
            """
            Formats comments into a readable string with indentation based on depth.
            """
            formatted = []
            indent = "  " * depth  # Indent based on nesting level
            for comment in comments:
                formatted.append(
                    f"{indent}Author: {comment['author']}\n{indent}Comment: {comment['body']}\n"
                )
                # Format replies recursively
                if comment["replies"]:
                    formatted.append(format_comments(comment["replies"], depth + 1))
            return "\n".join(formatted)

        url = self.COMMENTS_URL_TEMPLATE.format(postid=postid)
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch conversation: {response.status_code} {response.text}")

        data = response.json()
        post_data = data[0]['data']['children'][0]['data']
        comments_data = data[1]['data']['children']

        # Extract comments
        extracted_comments = extract_comments(comments_data)

        # Format post and comments
        post_str = (
            f"Title: {post_data['title']}\n"
            f"Author: {post_data.get('author', '[deleted]')}\n"
            f"Post Text: {post_data.get('selftext', '')}\n\n"
            "Comments:\n"
        )
        comments_str = format_comments(extracted_comments)
        result = post_str + comments_str

        return result
