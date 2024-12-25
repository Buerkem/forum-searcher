from Forum import Forum
import requests
import os

class Reddit(Forum):
    BASE_URL = "https://oauth.reddit.com/r/leetcode/new"
    COMMENTS_URL_TEMPLATE = "https://oauth.reddit.com/r/leetcode/comments/{postid}/"

    def __init__(self, access_token: str):
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def fetch_posts(self, filter_keyword: str="", start_page: int=1, end_page: int=2):
        """
        Fetch posts from LeetCode discussions between start and end pages.
        Returns a list of dictionaries containing post details.
        """
        after = None
        posts = []

        for page in range(start_page, end_page + 1):
            params = {"limit": 100}
            if after:
                params["after"] = after

            response = requests.get(self.BASE_URL, headers=self.headers, params=params)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch posts: {response.status_code} {response.text}")

            data = response.json()
            posts.extend([
                {"title": post["data"]["title"], "postid": f"https://reddit.com{post['data']['permalink']}", "id": post["data"]["id"]}
                for post in data["data"]["children"]
            ])

            after = data["data"]["after"]
            if not after:
                break  # End of pages

        return posts

    def fetch_conversation(self, postid: str, max_comments: int = 50, max_nesting: int = 6):
        """
        Fetches the conversation for a specific LeetCode discussion.
        Returns the conversation as a hierarchical JSON-like structure.
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

        url = self.COMMENTS_URL_TEMPLATE.format(postid=postid)
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch conversation: {response.status_code} {response.text}")

        data = response.json()
        post_data = data[0]['data']['children'][0]['data']
        comments_data = data[1]['data']['children']

        # Construct the structured result
        result = {
            "post": {
                "title": post_data['title'],
                "text": post_data.get('selftext', ''),
                "author": post_data.get('author', '[deleted]'),
            },
            "comments": extract_comments(comments_data)
        }

        return result
