# 卢怡然_C4D_agent-skill 代码说明

## 文件结构

```
卢怡然_C4D_agent-skill/
├── config.py              # 配置文件（模型名称、API地址、提示词、坐标等）
├── sias_agent.py          # 主程序入口（Agent核心逻辑）
├── map_generator.py       # 地图生成模块（Folium）
├── requirements.txt       # Python 依赖清单
├── README.md              # 本文件
└── raw_model_output.log   # 模型原始输出日志（运行后自动生成）
```

## 快速运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 确保 Ollama 已运行并加载模型
ollama serve
ollama pull gemma4:e4b

# 3. 运行 Agent（会自动调用本地模型并生成地图）
python sias_agent.py
```

## 代码产物 vs 手动截图补充

| 类型 | 内容 | 说明 |
|------|------|------|
| **代码产物** | sias_agent.py, map_generator.py, config.py, requirements.txt | 本项目源代码 |
| **代码产物** | 卢怡然_C4D_map.html | 运行代码后自动生成的地图文件 |
| **代码产物** | raw_model_output.log | 运行代码后自动生成的模型原始输出日志 |
| **代码产物** | 卢怡然_C4D_AI日志.md | 运行代码后自动生成的AI对话日志 |
| **手动截图补充** | output_screenshots/ 中的截图 | 需用户本地运行后手动截图填入 |
