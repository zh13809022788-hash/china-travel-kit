"""chinatripbox.com 自动发布流水线。

模块划分:
    config    读取 config.toml + 环境变量密钥
    topics    选题队列: 取题 / 去重 / 标记已用
    generator 调 Claude API 原创重写, 组装 frontmatter + slug
    publisher 写 .md, git commit/push, 批内随机延时
    indexing  百度普通收录推送(+可选 IndexNow), 失败重试1次
    logger    结构化日志 + 当天发布状态
    run       主流程编排(单个时段执行一次)
"""

__version__ = "1.0.0"
