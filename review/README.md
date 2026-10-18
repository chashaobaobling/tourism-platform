# 评论审核工作台

## 流程

CSV 上传、Selenium 爬虫和手动添加都会先写入 `data/review_staging.sqlite3`。批次完成模型评估后，评分与模型类别一致且置信度达到阈值的记录可自动通过；其他记录进入人工队列。正式 `comments` 表只在用户点击“确认并写入数据库”后更新。

暂存区保留输入评分、模型类别、置信度、一致性、人工决定、修订评分及写入后的 `comments.id`。正式表目前只保存原有字段；用户选择“确认模型类”时保留数字评分，并把确认类别留在暂存审核记录中。只有“改分通过”会改变正式表的 `sentiment_score`。

## 当前模型

`models/sentiment_model.keras` 是双输入 BERT 分类模型，输入为 `input_ids` 和 `attention_mask`，长度为 100，输出顺序为 `[差评, 中评, 好评]`。适配器使用 `BertTokenizer`；词表需要包含 `vocab.txt`。

默认分词器目录为 `D:\python_project\bert-base-chinese-model`，也可在 `.env` 中配置：

```text
REVIEW_MODEL_PATH=models/sentiment_model.keras
REVIEW_TOKENIZER_PATH=D:\python_project\bert-base-chinese-model
REVIEW_MAX_SEQUENCE_LENGTH=100
REVIEW_CONFIDENCE_THRESHOLD=0.65
```

当前项目 Python 环境需要通过 `requirements-review.txt` 安装审核、爬虫及模型依赖。TensorFlow 或 Transformers 不可用时，导入批次仍留在暂存区，但模型评估失败，禁止发布。

## 评论身份与更新

指纹由规范化后的景点名称、评论正文、昵称和评论日期组成，不包含评分和来源。数据库盘点发现部分完全相同的身份组合对应多行，因此没有为旧表强加唯一索引。发布时重新扫描并核对当前数据库：唯一匹配只更新确认后的评分；无匹配则新增；多个候选、批次内重复或缺少稳定身份信息会暂停并要求人工处理。CSV 的“序号”不会被当作 `comments.id`。

发布使用 MySQL 命名锁串行执行，并在单个事务中写入。评论正文、昵称、日期和原有主键不会因评分修正而改变。正式表写入失败时事务回滚，暂存审核记录仍保留。

`database.py` 的旧直写方法和爬虫命令行入口已停用直接写库；`preprocess_all.py` 也改为创建审核批次。数据库为空时，应用启动不会再自动从 CSV 导入。
