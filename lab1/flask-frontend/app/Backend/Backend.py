import json
import time

class Database:

    def __init__(self):
        """
        Initializes the database connection and creates a table if it doesn't exist.
        """
        pass

    def handle_request(self, request):
        """
        Handles incoming requests and returns a response.
        
        Args:
            request (json): The incoming request containing method, path, and body.
        
        Returns:
            json: The response to be sent back to the client.
        """
        time.sleep(2)  # Simulate a delay for processing the request

        response = {
            "status" : 200,
            "data" : [
                {"post_id" : "1", "title" : "Post 1", "content" : "Content of post 1"},
                {"post_id" : "2", "title" : "Post 2", "content" : "Content of post 2"},
                {"post_id" : "3", "title" : "Post 3", "content" : "Content of post 3"},
                {"post_id" : "4", "title" : "Post 4", "content" : "Content of post 4"},
                {"post_id" : "5", "title" : "Post 5", "content" : "Content of post 5"},
            ]
        }
        return response