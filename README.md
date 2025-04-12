# DatabaseLab

这是北京大学数据库概论2025春的实习

## 实习1

### 简介

仿照虎扑评分的业务功能设计的数据库系统，保留了主要的发起评分、用户评分、用户评论的功能。具体设计参见docs下文档。

### flask-frontend

基于Flask的简易前端展示，包含了如下8个使用场景的基础展示：
{}代表要提供的内容（由于工程量限制，请自行修改初始数据以及记忆id）

1. 用户发布帖子
{
“user_id",
“topic_id": [string],
“title",
}
2. 用户发布帖子关联的评分对象
{
“post_id",
“name",
“description", 
}
3. 用户对帖子的评分对象评论，并评分
{
“post_id",
“target_id",
“user_id",
“content",
“score": int
}
4. 用户对帖子的评分对象的评论评论
{
“post_id",
“target_id",
“user_id",
“content",
“parent", 
}

5. 查询主题下的帖子
{
“topic_id",
}

6. 查询帖子评分对象的平均分
{
“post_id",
“target_id",
}

7. 查询帖子评分对象下的评论
{
“post_id",
“target_id",
}

8. 查询用户记录
{
“user_id",
}

具体使用方法参见flask-frontend下的README.md
