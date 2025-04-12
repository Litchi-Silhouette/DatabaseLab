from .DataBase import getDB

def handle_request(request):
    """
    Handles incoming requests and returns a response.
    
    Args:
        request (dict): The incoming request containing method, path, and body.
    
    Returns:
        dict: The response to be sent back to the client.
    """
    return handle_request0(request, getDB())

def handle_request0(request, conn):
    response = {}
    try :
        req_type = request["req_type"]
        check_value(req_type, [
                "reg_user",
                "reg_topic",
                "post_post", 
                "post_target", 
                "post_comment_score", 
                "post_comment_comment", 
                "req_topic_posts", 
                "req_target_avgscore", 
                "req_target_comments", 
                "req_user_actions"
            ]
        )
        exec(f'''response["data"] = handle_{req_type}(request, conn)''')
        response["message"] = ""
        response["status"] = 200
    
    except Exception as ex: 
        response["message"] = str(ex)
        response["status"] = 100
    return response

def handle_reg_user(request, conn):
    user_nickname = check_type(request["user_nickname"], ["str"])
    cursor = conn.cursor()
    cursor.execute(
    f'''
    INSERT INTO User (Nickname) 
    VALUES (?)
    RETURNING UserID
    ''', (user_nickname,)
    )
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return {
        "user_id" : result[0]
    }
    
def handle_reg_topic(request, conn):
    topic_name = check_type(request["topic_name"], ["str"])
    cursor = conn.cursor()
    cursor.execute(
    '''
    INSERT INTO Topic (TopicName)
    VALUES (?)
    RETURNING TopicID
    ''',( topic_name,)
    )
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return {
        "topic_id": result[0]
    }


def handle_post_post(request, conn):
    user_id = check_type(request["user_id"], ["str", "int"])
    topic_id = check_type(request["topic_id"], ["str", "int"], True)
    title = check_type(request["title"], ["str"])
    cursor = conn.cursor()
    cursor.execute(
    f'''
    INSERT INTO Post (UserID, Title) 
    VALUES (?, ?)
    RETURNING PostID
    ''', (int(user_id),title,)
    )
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    for topic in topic_id:
        cursor = conn.cursor()
        cursor.execute(
        '''
        INSERT INTO PostTopic (PostID, TopicID)
        VALUES (?, ?)
        ''',(result[0], int(topic),)
        )
    cursor = conn.cursor()
    cursor.execute(
    '''
    INSERT INTO UserActionLog (UserID, ActionType, TargetType, TargetID)
    VALUES (?, ?, ?, ?)
    ''',(int(user_id), "CREATE_POST", "post", int(result[0]))
    )
    return {
        "post_id": result[0]
    }

def handle_post_target(request, conn):
    post_id = check_type(request["post_id"], ["str", "int"])
    name = check_type(request["name"], ["str"])
    description = check_type(request["description"], ["str"])
    cursor = conn.cursor()
    cursor.execute(
    '''
    INSERT INTO ScoreTarget (PostID, TargetName, Description) 
    VALUES (?, ?, ?)
    RETURNING TargetID
    ''',
    (int(post_id), name, description)
    )
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return {
        "target_id" : result[0]
    }

def handle_post_comment_score(request, conn):
    post_id = check_type(request["post_id"], ["str", "int"])
    target_id = check_type(request["target_id"], ["str", "int"])
    user_id = check_type(request["user_id"], ["str", "int"])
    content = check_type(request["content"], "str")
    score = check_type(request["score"], ["int"])
    
    cursor = conn.cursor()
    cursor.execute(
    '''
    INSERT INTO ScoreRecord (UserID, TargetID, PostID, Score)
    VALUES (?, ?, ?, ?)
    RETURNING RecordID
    '''
    ,(int(user_id), int(target_id), int(post_id), score,)
    )
    result1 = cursor.fetchone()
    cursor.execute(
    '''
    INSERT INTO Comment (PostID, UserID, Content, TargetID)
    VALUES (?, ?, ?, ?)
    RETURNING CommentID
    '''
    ,(int(post_id), int(user_id), content, int(target_id))
    )
    result2 = cursor.fetchone()
    cursor.execute(
    '''
    INSERT INTO UserActionLog (UserID, ActionType, TargetType, TargetID)
    VALUES (?, ?, ?, ?)
    ''',(int(user_id), "SCORE", "target", int(target_id))
    )
    cursor.execute(
    '''
    INSERT INTO UserActionLog (UserID, ActionType, TargetType, TargetID)
    VALUES (?, ?, ?, ?)
    ''',(int(user_id), "COMMENT", "comment", int(result2[0]))
    )
    conn.commit()
    cursor.close()
    return {
        "record_id" : result1[0],
        "comment_id": result2[0]
    }
    
def handle_post_comment_comment(request, conn):
    post_id = check_type(request["post_id"], ["str", "int"])
    target_id = check_type(request["target_id"], ["str", "int"])
    user_id = check_type(request["user_id"], ["str", "int"])
    content = check_type(request["content"], ["str"])
    parent = check_type(request["parent"], ["str", "int"])
    cursor = conn.cursor()
    cursor.execute(
    '''
    INSERT INTO Comment (PostID, UserID, Content, TargetID, ParentID)
    VALUES (?, ?, ?, ?, ?)
    RETURNING CommentID
    '''
    ,(int(post_id), int(user_id), content, int(target_id), int(parent))
    )
    result2 = cursor.fetchone()
    cursor.execute(
    '''
    INSERT INTO UserActionLog (UserID, ActionType, TargetType, TargetID)
    VALUES (?, ?, ?, ?)
    ''',(int(user_id), "COMMENT", "comment", int(result2[0]))
    )
    conn.commit()
    cursor.close()
    return {
        "comment_id": result2[0]
    }
    
def handle_req_topic_posts(request, conn):
    topic_id = check_type(request["topic_id"], ["str", "int"])
    cursor = conn.cursor()
    cursor.execute(
    f'''
    SELECT Post.* 
    FROM Post
    JOIN PostTopic USING(PostID)
    WHERE PostTopic.TopicID = {topic_id}
    '''
    )
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    return [
            {
                "post_id": a,
                "user_id": b,
                "title": c,
                "post_time": d
            }
            for a,b,c,d in result
        ]
    
def handle_req_target_avgscore(request, conn):
    post_id = check_type(request["post_id"], ["str", "int"])
    target_id =check_type(request["target_id"], ["str", "int"])
    cursor = conn.cursor()
    cursor.execute(
    f'''
    SELECT AVG(Score)
    FROM ScoreRecord
    WHERE ScoreRecord.PostID == {str(post_id)} and ScoreRecord.TargetID == {str(target_id)}
    '''
    )
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return {
        "score": result[0]
    }
    
def handle_req_target_comments(request, conn):
    post_id = check_type(request["post_id"], ["str", "int"])
    target_id =check_type(request["target_id"], ["str", "int"])
    cursor = conn.cursor()
    cursor.execute(
    f'''
    SELECT c.CommentID, c.UserID, c.Content, c.ParentID, c.CommentTime
    FROM Comment AS c
    WHERE c.PostID = {str(post_id)} and c.TargetID = {str(target_id)}
    '''
    )
    val = cursor.fetchall()
    conn.commit()
    cursor.close()
    return [
        {
            "comment_id": a,
            "user_id": b,
            "content": c,
            "parent_id": d,
            "comment_time": e
        }
        for a,b,c,d,e in val
    ]
    
def handle_req_user_actions(request, conn):
    user_id = check_type(request["user_id"], ["str", "int"])
    cursor = conn.cursor()
    cursor.execute(
    f''' 
    SELECT u.ActionType, u.LogID, u.ActionTime
    FROM UserActionLog AS u
    WHERE u.UserID = {str(user_id)}
    '''
    )
    val = cursor.fetchall()
    conn.commit()
    cursor.close()
    return [
        {
            "action_type": a,
            "action_id": b,
            "action_time": c,
        }
        for a,b,c in val
    ]


def check_value(param, valid_values):
    def _check_value(param, valid_values):
        if param not in valid_values:
            raise ValueError(f"{param} is not supported, it should be the " f"subset of {valid_values}.")

    if isinstance(param, list):
        for p in param:
            _check_value(p, valid_values)
    else:
        _check_value(param, valid_values)
    return param

def check_type(param, types, elem = False):
    def _check_type(param, types):
        if type(param).__name__ not in types:
            raise TypeError(f"{param} is of type{type(param)} not " f"supported, should be one of type {types}.")

    if isinstance(param, list) and elem:
        for p in param:
            _check_type(p, types)
    else:
        _check_type(param, types)
    return param