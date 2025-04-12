from ..Backend import handle_request, handle_request0,createDB, displayDB

tests = list()

class DBTest:
    def __init__(self, callback):
        self.conn = createDB()
        self.users = ["user1", "user2", "user3", "user4", "userA", "userB", "userC", "userD", "userE"]
        self.topics = ["tp1", "tp2", "tp3", "tpA", "tpB", "tpC"]
        self.callback = callback
    
    

    def test(test_case):
        def test_wrapper(*args, **kargs):
            args[0].callback(f"进行测试: {test_case.__name__.removeprefix('test_')}")
            val =  test_case(*args, **kargs)
            args[0].callback(f"通过测试: {test_case.__name__.removeprefix('test_')}")
            return val
        global tests 
        tests.append(test_wrapper)
        return test_wrapper
        
    def display(self):
        displayDB(self.conn, callback=self. callback)
    
    
    @staticmethod
    def errorOrData(responce):
        if responce["status"] != 200:
            raise Exception("Error in sql:"+ responce["message"])
        else:
            return responce["data"]
    
    def autotest(self):
        global tests
        for test in  tests:
            test(self)
     
    def test_main(self):
        self.test_reg_user()
        self.test_reg_topic()
        self.callback("数据库初始化测试完成")
        # self.display()
        self.test_post_post()
        self.test_post_target()
        self.test_post_comment_score()
        self.test_post_comment_comment()
        self.display()
        self.callback("数据库插入功能测试完成")
        self.test_req_topic_posts()
        self.test_req_target_avgscore()
        self.test_req_target_comments()
        self.test_req_user_actions()
        
    @test
    def test_reg_user(self):
        for index, nickname in enumerate(self.users):
            data = DBTest.errorOrData( handle_request0({
                "req_type": "reg_user",
                "user_nickname": nickname
            }, self.conn))
            assert data["user_id"] == index +1

    @test
    def test_reg_topic(self):
        for index, nickname in enumerate(self.topics):
            data = DBTest.errorOrData( handle_request0({
                "req_type": "reg_topic",
                "topic_name": nickname
            }, self.conn))
            assert data["topic_id"] == index +1
    
    @test
    def test_post_post(self):
        user_id = 2
        topic_id = [1,3,5]
        request = {
            "req_type": "post_post",
            "user_id" : str(user_id),
            "topic_id" : topic_id,
            "title" : "test_title"
        }
        data = DBTest.errorOrData(
            handle_request0(
                request,
                self.conn
            )
        )
        assert data["post_id"] == 1
    
    @test
    def test_post_target(self):
        post_id = 1
        name = "game score"
        description = "this is a ****ing game which you can give him a rating score\nand this is a ****ing two line description"
        request = {
            "req_type": "post_target",
            "post_id": str(post_id),
            "name": name,
            "description": description
        }
        data = DBTest.errorOrData(
            handle_request0(
                request,
                self.conn
            )
        )
        assert data["target_id"] == 1
        
    @test
    def test_post_comment_score(self):
        post_id = 1
        target_id = 1
        user_id = 4
        content = "狗屎游戏,狗都不玩"
        score = 0
        request = {
            "req_type": "post_comment_score",
            "post_id": post_id,
            "target_id": target_id,
            "user_id": user_id,
            "content": content,
            "score": score
        }
        data = DBTest.errorOrData(
            handle_request0(
                request,
                self.conn
            )
        )
        assert data["record_id"] == 1
        assert data["comment_id"] == 1
        cursor = self.conn.cursor()
        cursor.execute(
        f'''
        SELECT ParentID
        FROM Comment
        WHERE CommentID = {data["comment_id"]}
        '''
        )
        assert cursor.fetchall()[0][0] == None
        self.conn.commit()
        post_id = 1
        target_id = 1
        user_id = 5
        content = "狗屎游戏,我不玩"
        score = 1
        request = {
            "req_type": "post_comment_score",
            "post_id": post_id,
            "target_id": target_id,
            "user_id": user_id,
            "content": content,
            "score": score
        }
        data = DBTest.errorOrData(
            handle_request0(
                request,
                self.conn
            )
        )
        
    @test
    def test_post_comment_comment(self):
        post_id = 1
        target_id = 1
        user_id = 3
        content = "确实, rnm退钱"
        parent = 1
        request = {
            "req_type": "post_comment_comment",
            "post_id": post_id,
            "target_id": target_id,
            "user_id": user_id,
            "content": content,
            "parent": parent
        }
        data = DBTest.errorOrData(
            handle_request0(
                request,
                self.conn
            )
        )
        assert data["comment_id"] == 3
        cursor = self.conn.cursor()
        cursor.execute(
        f'''
        SELECT ParentID
        FROM Comment
        ORDER BY CommentID
        '''
        )
        all = cursor.fetchall()
        assert all[0][0] == None and all[1][0] == None and all[2][0] == parent
        self.conn.commit()
        
    @test
    def test_req_topic_posts(self):
        topic = 3
        data = DBTest.errorOrData(
            handle_request0(
                request= {
                    "req_type": "req_topic_posts",
                    "topic_id" : topic
                },
                conn= self.conn
            )
        )
        assert data[0]["title"] == "test_title"
    
    @test
    def test_req_target_avgscore(self):
        post_id = 1
        target_id = 1
        request = {
            "req_type": "req_target_avgscore",
            "post_id": post_id,
            "target_id": target_id
        }
        data = DBTest.errorOrData(
            handle_request0(
                request,
                self.conn
            )
        )
        assert data["score"] == 0.5

    @test 
    def test_req_target_comments(self):
        post_id = 1
        target_id = 1
        request = {
            "req_type": "req_target_comments",
            "post_id": post_id,
            "target_id": target_id
        }
        data = DBTest.errorOrData(
            handle_request0(
                request,
                self.conn
            )
        )
        assert len(data) == 3
        
    @test 
    def test_req_user_actions(self):
        user_id = 5
        request = {
            "req_type": "req_user_actions",
            "user_id": user_id
        }
        data = DBTest.errorOrData(
            handle_request0(
                request,
                self.conn
            )
        )
        assert len(data) == 2
        
    