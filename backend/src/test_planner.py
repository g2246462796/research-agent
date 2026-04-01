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
    raw_response = """=== Planner raw output ===
```json
{
  "tasks": [
    {
      "title": "技术架构突破",
      "intent": "梳理2026年多模态模型的核心技术进展，包括架构创新、训练方法、模态融合机制等",
      "query": "2026 multimodal model architecture breakthrough, vision-language transformer advances, cross-modal fusion techniques 2026"
    },
    {
      "title": "应用场景落地",
      "intent": "调研多模态技术在各行业的实际部署案例，识别成熟应用与新兴场景",
      "query": "multimodal AI applications 2026, real-world deployment cases, industry use cases vision-language models"
    },
    {
      "title": "性能基准评估",
      "intent": "收集主流多模态模型的评测结果与基准测试数据，对比性能指标",
      "query": "multimodal benchmark 2026, MMBench VQA evaluation results, model performance comparison"
    },
    {
      "title": "行业生态格局",
      "intent": "分析主要研究机构与企业的多模态布局，识别关键玩家与竞争态势",
      "query": "multimodal AI companies 2026, research labs vision-language, industry landscape competitive analysis"
    },
    {
      "title": "挑战趋势展望",
      "intent": "总结当前技术瓶颈与未来发展方向，预测2026-2027演进趋势",
      "query": "multimodal AI challenges 2026, future research directions, limitations and opportunities vision-language"
    }
  ]
}
```

[TOOL_CALL:note:{"action":"create","task_id":1,"title":"任务1: 技术架构突破","note_type":"task_state","tags":["deep_research","task_1"],"content":"任务目标：梳理2026年多模态模型核心技术进展。检索方向：架构创新、训练方法、模态融合机制。状态：待执行"}]

[TOOL_CALL:note:{"action":"create","task_id":2,"title":"任务2: 应用场景落地","note_type":"task_state","tags":["deep_research","task_2"],"content":"任务目标：调研多模态技术各行业实际部署案例。检索方向：商业应用、新兴场景、成熟落地案例。状态：待执行"}]

[TOOL_CALL:note:{"action":"create","task_id":3,"title":"任务3: 性能基准评估","note_type":"task_state","tags":["deep_research","task_3"],"content":"任务目标：收集主流多模态模型评测结果与基准数据。检索方向：MMBench、VQA、性能对比指标。状态：待执行"}]

[TOOL_CALL:note:{"action":"create","task_id":4,"title":"任务4: 行业生态格局","note_type":"task_state","tags":["deep_research","task_4"],"content":"任务目标：分析主要研究机构与企业的多模态布局。检索方向：关键玩家、竞争态势、研发投入。状态：待执行"}]

[TOOL_CALL:note:{"action":"create","task_id":5,"title":"任务5: 挑战趋势展望","note_type":"task_state","tags":["deep_research","task_5"],"content":"任务目标：总结技术瓶颈与未来发展方向。检索方向：当前局限、2026-2027演进趋势、开放问题。状态：待执行"}]
=== End of raw output ===
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