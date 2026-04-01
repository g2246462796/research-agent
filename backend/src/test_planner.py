import json
from services.planner import PlanningService
from config import Configuration
from models import SummaryState
from dotenv import load_dotenv

load_dotenv()

def test_parse():
    config = Configuration.from_env()
    # 创建一个模拟的 PlanningService，但不需要真正的 agent
    # 我们直接测试解析函数
    planner = PlanningService(planner_agent=None, config=config)  # 注意：我们不会调用 agent，只测试解析方法

    # 模拟从模型返回的原始输出（包含多个 TOOL_CALL 和最终 JSON）
    raw_response = """[TOOL_CALL:note:{"action":"create","task_id":1,"title":"任务 1: 多模态进展概览","note_type":"task_state","tags":["deep_research","task_1"],"content":"梳理多模态AI近年来的整体发展脉络，包括关键里程碑、主流技术路线和代表性模型。"}]

[TOOL_CALL:note:{"action":"create","task_id":2,"title":"任务 2: 核心技术突破","note_type":"task_state","tags":["deep_research","task_2"],"content":"聚焦多模态融合、对齐与推理方面的关键技术突破，如跨模态表示学习、大模型架构创新等。"}]

[TOOL_CALL:note:{"action":"create","task_id":3,"title":"任务 3: 应用场景落地","note_type":"task_state","tags":["deep_research","task_3"],"content":"调研多模态技术在实际场景中的应用进展，如智能助手、医疗影像、自动驾驶、内容生成等。"}]

[TOOL_CALL:note:{"action":"create","task_id":4,"title":"任务 4: 挑战与未来方向","note_type":"task_state","tags":["deep_research","task_4"],"content":"分析当前多模态研究面临的主要挑战（如数据稀缺、评估标准不一）及学术界/工业界提出的未来方向。"}]

{
  "tasks": [
    {
      "title": "多模态进展概览",
      "intent": "梳理多模态AI近年来的整体发展脉络，包括关键里程碑与主流技术路线。",
      "query": "multimodal AI recent advances overview survey 2024 2025"
    },
    {
      "title": "核心技术突破",
      "intent": "聚焦多模态融合、对齐与推理方面的关键技术突破，如跨模态表示学习与大模型架构。",
      "query": "multimodal fusion alignment representation learning foundation models breakthroughs"
    },
    {
      "title": "应用场景落地",
      "intent": "调研多模态技术在实际场景中的应用进展，如智能助手、医疗、自动驾驶等。",
      "query": "multimodal AI real-world applications healthcare autonomous driving content generation"
    },
    {
      "title": "挑战与未来方向",
      "intent": "分析当前多模态研究面临的主要挑战及学术界/工业界提出的未来发展方向。",
      "query": "challenges in multimodal AI future research directions limitations evaluation benchmarks"
    }
  ]
}
"""
    text = raw_response.strip()
    tmp = planner._extract_json_payload(text)
    # print(tmp)
    tasks = planner._extract_tasks(raw_response)
    print(f"解析出 {len(tasks)} 个任务:")
    for task in tasks:
        print(f"  - {task.get('title')}")

if __name__ == "__main__":
    test_parse()