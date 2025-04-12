import json
import time
def handle_request(request):
    """
    Handles incoming requests and returns a response.
    
    Args:
        request (dict): The incoming request containing method, path, and body.
    
    Returns:
        dict: The response to be sent back to the client.
    """
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
    time.sleep(2)  # Simulate a delay for processing the request
    return json.dumps(response)