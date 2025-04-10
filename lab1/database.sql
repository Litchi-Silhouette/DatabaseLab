User(
  UserID         INTEGER PRIMARY KEY,  -- 用户唯一标识
  Nickname       VARCHAR(50) NOT NULL,  -- 用户昵称（需唯一性约束）
  Level          INTEGER DEFAULT 1,     -- 用户等级
  RegisterTime   DATETIME NOT NULL      -- 注册时间
)
Topic(
  TopicID        INTEGER PRIMARY KEY,  -- 主题唯一标识
  TopicName      VARCHAR(30) NOT NULL   -- 主题名称（如NBA/影视）
)
Post(
  PostID         INTEGER PRIMARY KEY,   -- 帖子唯一标识
  UserID         INTEGER NOT NULL,      -- 发帖人
  Title          VARCHAR(200) NOT NULL, -- 帖子标题
  PublishTime    DATETIME NOT NULL,     -- 发布时间
  FOREIGN KEY (UserID) REFERENCES User(UserID)
)
PostTopic(
  PostID         INTEGER NOT NULL,      -- 关联帖子
  TopicID        INTEGER NOT NULL,      -- 关联主题
  PRIMARY KEY (PostID, TopicID),
  FOREIGN KEY (PostID) REFERENCES Post(PostID),
  FOREIGN KEY (TopicID) REFERENCES Topic(TopicID)
)
ScoreTarget(
  TargetID       INTEGER PRIMARY KEY,   -- 评分对象唯一标识
  TargetName     VARCHAR(100) NOT NULL, -- 对象名称（如詹姆斯/iPhone15）
  Description    TEXT,                  -- 对象简介
  FOREIGN KEY (PostID) REFERENCES Post(PostID)
)
ScoreRecord(
  RecordID       INTEGER PRIMARY KEY,   -- 评分记录唯一标识
  UserID         INTEGER NOT NULL,      -- 评分用户
  TargetID       INTEGER NOT NULL,      -- 被评对象
  PostID         INTEGER,               -- 关联帖子（可选）
  Score          DECIMAL(3,1) CHECK(Score BETWEEN 0 AND 10), -- 分数
  RecordTime     DATETIME NOT NULL,     -- 评分时间
  FOREIGN KEY (UserID) REFERENCES User(UserID),
  FOREIGN KEY (TargetID) REFERENCES ScoreTarget(TargetID),
  FOREIGN KEY (PostID) REFERENCES Post(PostID)
)
Comment(
  CommentID      INTEGER PRIMARY KEY,   -- 评论唯一标识
  PostID         INTEGER NOT NULL,      -- 所属帖子
  UserID         INTEGER NOT NULL,      -- 评论人
  Content        TEXT NOT NULL,         -- 评论内容
  ParentID       INTEGER,               -- 父评论ID（楼中楼结构）
  TargetID       INTEGER,               -- 关联的评分对象（可选）
  CommentTime    DATETIME NOT NULL,     -- 评论时间
  FOREIGN KEY (PostID) REFERENCES Post(PostID),
  FOREIGN KEY (UserID) REFERENCES User(UserID),
  FOREIGN KEY (ParentID) REFERENCES Comment(CommentID),
  FOREIGN KEY (TargetID) REFERENCES ScoreTarget(TargetID)
)
UserActionLog(
  LogID          INTEGER PRIMARY KEY,   -- 日志唯一标识
  UserID         INTEGER NOT NULL,      -- 操作用户
  ActionType     VARCHAR(20) NOT NULL,  -- 动作类型（发帖/评论/评分等）
  TargetType     VARCHAR(20) NOT NULL,  -- 目标类型（post/comment/target）
  TargetID       INTEGER NOT NULL,      -- 目标ID（如帖子ID/评论ID）
  ActionTime     DATETIME NOT NULL,     -- 操作时间
  FOREIGN KEY (UserID) REFERENCES User(UserID)
)
FavoritePost(
  UserID         INTEGER NOT NULL,      -- 收藏用户
  PostID         INTEGER NOT NULL,      -- 被收藏帖子
  FavoriteTime   DATETIME NOT NULL,     -- 收藏时间
  PRIMARY KEY (UserID, PostID),
  FOREIGN KEY (UserID) REFERENCES User(UserID),
  FOREIGN KEY (PostID) REFERENCES Post(PostID)
)
Like(
  UserID         INTEGER NOT NULL,      -- 点赞用户
  CommentID      INTEGER NOT NULL,      -- 被赞评论
  LikeTime       DATETIME NOT NULL,     -- 点赞时间
  PRIMARY KEY (UserID, CommentID),
  FOREIGN KEY (UserID) REFERENCES User(UserID),
  FOREIGN KEY (CommentID) REFERENCES Comment(CommentID)
)