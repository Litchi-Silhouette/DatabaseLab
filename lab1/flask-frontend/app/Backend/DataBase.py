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