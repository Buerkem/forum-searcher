from abc import ABC, abstractmethod
from typing import List, Dict

class Forum(ABC):
    @abstractmethod
    def fetch_posts(self, filter_keyword:str = "", start_page: int=1, end_page: int=2) -> List[Dict[str, str]]:
        """
        Fetch posts from the forum between start and end pages.
        Returns a list of dictionaries containing 'topic_id' and 'topic_title'.
        The returned list should have the format:
        [{"topic_id": "id_1", "topic_title": "Title 1"}, {"topic_id": "id_2", "topic_title": "Title 2"}]
        """
        pass

    @abstractmethod
    def fetch_conversation(self, topic_id: str, max_comments: int = 50, max_nesting: int = 6) -> str:
        """
        Fetch the conversation for a specific topic.
        Returns the conversation text as a string.
        
        'max_comments' limits the number of comments (or replies) retrieved, typically used for pagination.
        'max_nesting' controls the depth of nested comments:
            - A value of 1 retrieves the main topic and its direct replies.
            - A value of 2 retrieves the main topic, direct replies, and replies to those replies, and so on.
        """
        pass
