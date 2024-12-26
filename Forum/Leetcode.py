import requests
import json
from Forum.Forum import Forum

class Leetcode(Forum):
    BASE_URL = "https://leetcode.com/graphql"

    def get_main_post(self, topic_id):
        query = """
        query DiscussTopic($topicId: Int!) {
        topic(id: $topicId) {
            post {
            content
            author {
                username
                id
            }
            }
        }
        }
        """
        
        variables = {"topicId": topic_id}
        payload = {"query": query, "variables": variables}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(self.BASE_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if the data contains the expected keys
            if data and 'data' in data and 'topic' in data['data'] and 'post' in data['data']['topic']:
                post_data = data['data']['topic']['post']
                content = post_data.get('content', 'No content available')
                
                # Check if 'author' exists; if not, use a fallback
                author = post_data.get('author', None)
                if author is None:
                    author_name = 'anonymous_user'  # Fallback username
                    author_id = 'unknown'           # Fallback author ID
                else:
                    author_name = author.get('username', 'anonymous_user')  # Fallback to 'anonymous_user'
                    author_id = author.get('id', 'unknown')  # Fallback to 'unknown'
                
                main_post = {"author": {"username": author_name, "id": author_id}, "content": content}
                return main_post
            else:
                print(f"Error: No post data available for topic_id {topic_id}")
                return None
        else:
            print(f"Error: {response.status_code}")
            return None

    def get_comments(self, topic_id, order_by="best", page_no=1, num_per_page=10):
        query = """
        query discussComments($topicId: Int!, $orderBy: String = "newest_to_oldest", $pageNo: Int = 1, $numPerPage: Int = 10) {
        topicComments(topicId: $topicId, orderBy: $orderBy, pageNo: $pageNo, numPerPage: $numPerPage) {
            data {
            post {
                content
                author {
                username
                }
            }
            }
        }
        }
        """
        
        variables = {
            "topicId": topic_id,
            "orderBy": order_by,
            "pageNo": page_no,
            "numPerPage": num_per_page
        }
        
        payload = {"query": query, "variables": variables}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(self.BASE_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if the response contains valid comments
            if 'data' in data and 'topicComments' in data['data'] and 'data' in data['data']['topicComments']:
                comments = data['data']['topicComments']['data']
                formatted_comments = []
                
                for comment in comments:
                    comment_data = comment['post']
                    author = comment_data.get('author', None)
                    if author is None:
                        author_username = 'anonymous_user'  # Fallback username
                    else:
                        author_username = author.get('username', 'anonymous_user')  # Fallback to 'anonymous_user'
                    
                    comment_info = {
                        "content": comment_data.get('content', 'No content available'),
                        "author_username": author_username
                    }
                    formatted_comments.append(comment_info)
                
                return formatted_comments
            else:
                print(f"Error: No comments found for topic_id {topic_id}")
                return []
        else:
            print(f"Error: {response.status_code}")
            return []

    def fetch_conversation(self, topic_id):
        main_post = self.get_main_post(topic_id)
        if main_post:
            comments = self.get_comments(topic_id)
            conversation = {
                "main_post": main_post,
                "comments": comments
            }
            return json.dumps(conversation, indent=4)
        else:
            return json.dumps({"error": "Unable to fetch the main post."}, indent=4)

    def fetch_posts(self, filter_keyword: str="", start_page: int=1, end_page: int=2):
        posts_per_page = 15
        skip = (start_page - 1) * posts_per_page #posts to skip depending to get to start post
        total_posts_to_fetch = (end_page - start_page + 1) * posts_per_page
        forum_link = "https://leetcode.com"
        query = """
        query categoryTopicList($categories: [String!]!, $first: Int!, $orderBy: TopicSortingOption, $skip: Int, $query: String, $tags: [String!]) {
            categoryTopicList(categories: $categories, orderBy: $orderBy, skip: $skip, query: $query, first: $first, tags: $tags) {
                edges {
                    node {
                        id
                        title
                    }
                }
            }
        }
        """
        
        variables = {
            "categories": ["interview-question"],
            "first": total_posts_to_fetch,
            "orderBy": "hot",
            "skip": skip,
            "query": filter_keyword,
            "tags": []
        }

        payload = {
            "operationName": "categoryTopicList",
            "query": query,
            "variables": variables
        }

        response = requests.post(self.BASE_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        filtered_discussions = []
        if data.get('data'):
            discussions = data['data']['categoryTopicList']['edges']
            for item in discussions:
                title = item['node']['title']
                post_id = item['node']['id']
                url = f"{forum_link}/discuss/interview-question/{post_id}"
                if filter_keyword.lower() in title.lower():
                    filtered_discussions.append({
                        "title" :  title,
                        "postid" : post_id,
                        "url" : url
                        }
                        )
        return filtered_discussions
