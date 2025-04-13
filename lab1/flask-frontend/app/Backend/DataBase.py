import sqlite3

DB_CONNECTION = None

def initDB(path =  ':memory:'):
    global DB_CONNECTION
    assert DB_CONNECTION is None
    DB_CONNECTION = createDB(path)

def shutdownDB():
    global DB_CONNECTION
    assert DB_CONNECTION is not None
    DB_CONNECTION.close()
    DB_CONNECTION = None
    
def getDB():
    global DB_CONNECTION
    assert DB_CONNECTION is not None
    return DB_CONNECTION

def createDB(path = ':memory:'):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()
    cursor.executescript('''
    -- 用户表：存储平台用户核心信息
    CREATE TABLE User (
    UserID         INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
    Nickname       VARCHAR(50) NOT NULL UNIQUE,       -- 昵称唯一约束
    Level          INTEGER DEFAULT 1 CHECK(Level > 0),-- 等级最小为1
    RegisterTime   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    -- 主题分类表：内容分类（如NBA/影视）
    CREATE TABLE Topic (
    TopicID        INTEGER PRIMARY KEY AUTOINCREMENT,
    TopicName      VARCHAR(30) NOT NULL UNIQUE,       -- 主题名唯一
    CreateTime     DATETIME DEFAULT CURRENT_TIMESTAMP -- 新增创建时间字段
    );

    -- 帖子表：用户发布的主题帖
    CREATE TABLE Post (
    PostID         INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID         INTEGER NOT NULL,
    Title          VARCHAR(200) NOT NULL CHECK(LENGTH(Title) >= 5), -- 标题长度限制
    PublishTime    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
    );

    -- 帖子-主题关联表（多对多关系）
    CREATE TABLE PostTopic (
    PostID         INTEGER NOT NULL,
    TopicID        INTEGER NOT NULL,
    PRIMARY KEY (PostID, TopicID),
    FOREIGN KEY (PostID) REFERENCES Post(PostID) ON DELETE CASCADE,
    FOREIGN KEY (TopicID) REFERENCES Topic(TopicID) ON DELETE RESTRICT
    );

    -- 评分对象表：需与帖子严格绑定
    CREATE TABLE ScoreTarget (
    TargetID       INTEGER PRIMARY KEY AUTOINCREMENT,
    PostID         INTEGER NOT NULL,                  -- 强制绑定到一个帖子
    TargetName     VARCHAR(100) NOT NULL CHECK(LENGTH(TargetName) >= 2),
    Description    TEXT,
    FOREIGN KEY (PostID) REFERENCES Post(PostID) ON DELETE CASCADE
    );

    -- 评分记录表：用户对对象的打分
    CREATE TABLE ScoreRecord (
    RecordID       INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID         INTEGER NOT NULL,
    TargetID       INTEGER NOT NULL,
    PostID         INTEGER NOT NULL,                  -- 冗余存储便于查询
    Score          DECIMAL(3,1) NOT NULL CHECK(Score BETWEEN 0 AND 10),
    RecordTime     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (TargetID) REFERENCES ScoreTarget(TargetID) ON DELETE CASCADE,
    FOREIGN KEY (PostID) REFERENCES Post(PostID) ON DELETE CASCADE,
    UNIQUE (UserID, TargetID)                         -- 防止重复评分
    );

    -- 评论表：支持楼中楼结构
    CREATE TABLE Comment (
    CommentID      INTEGER PRIMARY KEY AUTOINCREMENT,
    PostID         INTEGER NOT NULL,
    UserID         INTEGER NOT NULL,
    Content        TEXT NOT NULL CHECK(LENGTH(Content) >= 5),
    ParentID       INTEGER,                           -- 父评论ID实现嵌套
    TargetID       INTEGER,                           -- 可选关联评分对象
    CommentTime    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PostID) REFERENCES Post(PostID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (ParentID) REFERENCES Comment(CommentID) ON DELETE CASCADE,
    FOREIGN KEY (TargetID) REFERENCES ScoreTarget(TargetID) ON DELETE SET NULL
    );

    -- 用户行为日志表（审计用）
    CREATE TABLE UserActionLog (
    LogID          INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID         INTEGER NOT NULL,
    ActionType     VARCHAR(20) NOT NULL CHECK(ActionType IN (
        'CREATE_POST','COMMENT','SCORE','LIKE','FAVORITE')), -- 枚举约束
    TargetType     VARCHAR(20) NOT NULL CHECK(TargetType IN (
        'post','comment','target')),
    TargetID       INTEGER NOT NULL,
    ActionTime     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
    );

    -- 帖子收藏表
    CREATE TABLE FavoritePost (
    UserID         INTEGER NOT NULL,
    PostID         INTEGER NOT NULL,
    FavoriteTime   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (UserID, PostID),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (PostID) REFERENCES Post(PostID) ON DELETE CASCADE
    );

    -- 评论点赞表
    CREATE TABLE Like (
    UserID         INTEGER NOT NULL,
    CommentID      INTEGER NOT NULL,
    LikeTime       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (UserID, CommentID),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (CommentID) REFERENCES Comment(CommentID) ON DELETE CASCADE
    );
    ''')

    # 提交事务
    conn.commit()
    
    return conn

def displayDB(conn, callback):
    import pandas as pd
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    table_name = cursor.fetchall()
    for table in table_name:
        df = pd.read_sql_query(f"SELECT * FROM {table[0]}", con=conn)
        callback(df)

def init_sample_data():
    conn = getDB()
    cursor = conn.cursor()
    
    # 清空现有数据（测试用）
    cursor.execute("DELETE FROM Like")
    cursor.execute("DELETE FROM FavoritePost")
    cursor.execute("DELETE FROM UserActionLog")
    cursor.execute("DELETE FROM Comment")
    cursor.execute("DELETE FROM ScoreRecord")
    cursor.execute("DELETE FROM ScoreTarget")
    cursor.execute("DELETE FROM PostTopic")
    cursor.execute("DELETE FROM Post")
    cursor.execute("DELETE FROM Topic")
    cursor.execute("DELETE FROM User")

    # 1. 用户数据
    users = [
        ('虎扑JR123', 5),
        ('湖人总冠军', 3),
        ('数码评测君', 8),
        ('电影爱好者', 2),
        ('CBA观察员', 4)
    ]
    cursor.executemany('''
    INSERT INTO User (Nickname, Level) 
    VALUES (?, ?)
    ''', users)

    # 2. 主题数据
    topics = [
        ('NBA', '2023-01-01 00:00:00'),
        ('CBA', '2023-01-02 00:00:00'),
        ('影视', '2023-01-03 00:00:00'),
        ('数码', '2023-01-04 00:00:00')
    ]
    cursor.executemany('''
    INSERT INTO Topic (TopicName, CreateTime) 
    VALUES (?, ?)
    ''', topics)

    # 3. 帖子数据（每个用户至少2个帖子）
    posts = [
        (1, '湖人vs勇士全场集锦！詹姆斯关键三分', '2023-05-01 19:30:00'),
        (1, '约基奇最新赛季数据分析', '2023-05-02 14:00:00'),
        (2, 'iPhone15上手实测报告', '2023-05-03 10:15:00'),
        (3, '《流浪地球2》深度影评', '2023-05-04 20:45:00'),
        (4, 'CBA总决赛辽宁vs浙江前瞻', '2023-05-05 09:00:00'),
        (5, '小米13 Ultra相机评测', '2023-05-06 16:20:00')
    ]
    cursor.executemany('''
    INSERT INTO Post (UserID, Title, PublishTime) 
    VALUES (?, ?, ?)
    ''', posts)

    # 4. 帖子-主题关联
    post_topics = [
        (1, 1),  # NBA
        (2, 1),  # NBA
        (3, 4),  # 数码
        (4, 3),  # 影视
        (5, 2),  # CBA
        (6, 4)   # 数码
    ]
    cursor.executemany('''
    INSERT INTO PostTopic (PostID, TopicID) 
    VALUES (?, ?)
    ''', post_topics)

    # 5. 评分对象（每个帖子2个对象）
    score_targets = [
        (1, '勒布朗·詹姆斯', '湖人队核心球员'),
        (1, '斯蒂芬·库里', '勇士队当家球星'),
        (3, 'iPhone15 Pro', '苹果最新旗舰手机'),
        (3, '三星S23 Ultra', '安卓机皇'),
        (4, '《流浪地球2》', '中国科幻大片'),
        (5, '郭艾伦', '辽宁队后卫'),
        (6, '小米13 Ultra', '徕卡影像旗舰')
    ]
    cursor.executemany('''
    INSERT INTO ScoreTarget (PostID, TargetName, Description) 
    VALUES (?, ?, ?)
    ''', score_targets)

    # 6. 评分记录（每个对象3-5个评分）
    score_records = [
        (1, 1, 1, 9.5),
        (2, 1, 1, 8.8),
        (3, 1, 2, 9.0),
        (1, 3, 3, 9.2),
        (2, 3, 3, 8.5),
        (4, 3, 3, 7.9),
        (3, 4, 4, 9.7),
        (5, 6, 6, 9.4)
    ]
    cursor.executemany('''
    INSERT INTO ScoreRecord (UserID, TargetID, PostID, Score) 
    VALUES (?, ?, ?, ?)
    ''', score_records)

    # 7. 评论数据（含楼中楼）
    comments = [
        (1, 1, '詹姆斯今天太神了！', None, 1),
        (2, 1, '库里三分还是稳', None, 2),
        (3, 1, '裁判有几个判罚有问题', 1, 1),
        (4, 3, 'iPhone的录像功能确实强', None, 3),
        (6, 5, '小米这次影像进步很大', None, 7)
    ]
    cursor.executemany('''
    INSERT INTO Comment (PostID, UserID, Content, ParentID, TargetID) 
    VALUES (?, ?, ?, ?, ?)
    ''', comments)

    # 8. 收藏记录
    favorites = [
        (2, 1),
        (3, 3),
        (4, 4),
        (5, 6)
    ]
    cursor.executemany('''
    INSERT INTO FavoritePost (UserID, PostID) 
    VALUES (?, ?)
    ''', favorites)

    # 9. 点赞记录
    likes = [
        (2, 1),
        (3, 4),
        (4, 5)
    ]
    cursor.executemany('''
    INSERT INTO Like (UserID, CommentID) 
    VALUES (?, ?)
    ''', likes)

    # 10. 行为日志（自动生成）
    actions = [
        (1, 'CREATE_POST', 'post', 1),
        (2, 'COMMENT', 'comment', 1),
        (3, 'SCORE', 'target', 1),
        (4, 'FAVORITE', 'post', 3),
        (5, 'LIKE', 'comment', 5)
    ]
    cursor.executemany('''
    INSERT INTO UserActionLog (UserID, ActionType, TargetType, TargetID) 
    VALUES (?, ?, ?, ?)
    ''', actions)

    conn.commit()
