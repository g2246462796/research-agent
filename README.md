本项目作为学习一些Agent教程后，靠自己实现的一个用于实习的Agent项目。

## 目录结构
AI RESEARCHER/    <--- 这是你的空文件夹，重命名为这个
├── .env                # 存放API Key（最重要）
├── main.py             # 项目入口，一键运行
├── requirements.txt    # 依赖清单
├── configs/            # 配置文件（模型、搜索）
│   └── config.yml
├── core/               # 核心逻辑（多智能体、意图判断）
│   ├── __init__.py
│   ├── agent.py        # 智能体基类
│   ├── orchestrator.py # 调度器（判断浅层/深度研究）
│   └── researcher.py    # 研究员（搜索+写报告）
├── models/             # 大模型适配层（替换国产API）
│   ├── __init__.py
│   └── llm.py          # 核心！封装国产大模型
├── tools/              # 工具层（替换国产搜索）
│   ├── __init__.py
│   ├── web_search.py   # 联网搜索
│   └── paper_search.py # 论文搜索
└── logs/               # 日志