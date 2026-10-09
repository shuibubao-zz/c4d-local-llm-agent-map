# 卢怡然_C4D_拿来说明

> 本文档说明项目使用的库清单、参考资料、功能边界。
> 学生：卢怡然 | 日期：2026年10月

---

## 一、项目使用库清单

### 1.1 Python 库

| 库名 | 版本要求 | 用途 | 是否必须 |
|------|---------|------|---------|
| `requests` | ≥2.28.0 | 调用 Ollama OpenAI 兼容 API（HTTP POST 请求） | 必须 |
| `folium` | ≥0.14.0 | 生成交互式 HTML 地图（基于 Leaflet.js） | 必须 |
| `json` | 内置 | 解析模型输出的 JSON 数据 | 内置 |
| `re` | 内置 | 正则表达式，用于 JSON 容错解析 | 内置 |
| `time` | 内置 | 计时，计算推理耗时和 tok/s | 内置 |
| `datetime` | 内置 | 日志时间戳 | 内置 |

### 1.2 Folium 插件（随 folium 安装）

| 插件 | 用途 |
|------|------|
| `folium.plugins.Fullscreen` | 全屏控制按钮 |
| `folium.plugins.MeasureControl` | 测距工具 |
| `folium.plugins.MousePosition` | 鼠标坐标显示 |

### 1.3 前端依赖（Folium 自动引入）

| 库 | 用途 | 来源 |
|------|------|------|
| Leaflet.js | 交互式地图前端框架 | CDN（Folium自动加载） |
| OpenStreetMap 瓦片 | 地图底图瓦片 | OpenStreetMap服务器 |
| Font Awesome | 标记点图标 | CDN |

### 1.4 本地工具

| 工具 | 版本 | 用途 |
|------|------|------|
| Ollama | 最新版 | 本地运行 Gemma 4 模型 |
| Python | ≥3.8 | 运行 Agent 代码 |
| 浏览器 | 任意现代浏览器 | 打开交互式地图 |

### 1.5 可选依赖（Level3/Level4 扩展用，当前未启用）

| 库 | 用途 | 安装命令 |
|------|------|---------|
| `psutil` | 获取设备CPU/内存信息 | `pip install psutil` |
| `nvidia-ml-py` | GPU监控（NVIDIA显卡） | `pip install nvidia-ml-py` |

---

## 二、参考资料

### 2.1 官方文档

| 资源 | 链接 | 参考内容 |
|------|------|---------|
| Ollama 官方 | https://ollama.com | Ollama安装、模型拉取 |
| Ollama Gemma 4 模型页 | https://ollama.com/library/gemma4 | Gemma 4 模型变体说明 |
| Ollama OpenAI 兼容 API | https://ollama.com/blog/openai-compatibility | API接口使用方法 |
| Folium 文档 | https://python-visualization.github.io/folium/ | 地图生成方法 |
| Leaflet.js | https://leafletjs.com/ | 前端地图交互 |
| Gemma 4 官方博客 | https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/ | 模型介绍 |

### 2.2 技术参考

| 资源 | 参考内容 |
|------|---------|
| OpenAI API 文档 | OpenAI 兼容 API 格式（/v1/chat/completions） |
| Python requests 库文档 | HTTP 请求方法 |
| JSON 规范 | JSON 数据格式标准 |
| 正则表达式文档 | re 模块使用方法 |

### 2.3 课程资料

| 资料 | 说明 |
|------|------|
| CHALLENGE.md | C4D 任务文档，定义任务要求和评分标准 |
| rubric.json | 官方评分标准（5个维度，100分） |
| challenge.yaml | 课程结构化定义 |
| C4D.pdf | 任务详细说明 |
| C4D 补充说明.pdf | 补充说明材料 |

---

## 三、功能边界说明

### 3.1 已完成功能

| 功能 | Level | 状态 | 说明 |
|------|-------|------|------|
| 本地模型部署 | Level1 | ✅ | Ollama + Gemma 4 E4B Q4_K_M |
| 基本对话能力 | Level1 | ✅ | 可通过 Ollama 进行对话 |
| 结构化JSON输出 | Level2 | ✅ | 系统提示词约束 + 5层容错解析 |
| 交互式地图 | Level2 | ✅ | Folium生成，8个标记点，弹窗信息 |
| 完整Python源码 | Level2 | ✅ | 模块化设计，注释完整 |
| 异常处理 | Level2 | ✅ | 连接错误、超时、HTTP错误、JSON解析容错 |
| 对话日志 | Level2 | ✅ | 原始输出日志 + AI日志文档 |
| 多轮对话Agent | Level3 | ✅ | add新增 / modify修改标记点 |
| 扩展注释预留 | Level3 | ✅ | call_tool()多工具接口框架 |
| 多工具调用 | Level3 | 📋 预留 | 接口已定义，具体工具待实现 |
| 代码生成Agent | Level3 | ❌ | 本轮不做 |
| 视觉理解 | Level3 | ❌ | 本轮不做 |
| 模型对比报告 | Level4 | ❌ | 本轮不做 |
| 设备适配 | Level4 | ❌ | 本轮不做 |
| 量化对比 | Level4 | ❌ | 本轮不做 |
| Uncensored模型 | 加分 | ❌ | 本轮不做 |

### 3.2 本轮不做的功能及原因

| 功能 | 不做原因 |
|------|---------|
| 多工具调用实现 | 超出Level2要求，接口已预留，后续可扩展 |
| 代码生成Agent | 需要更复杂的Agent框架，超出当前范围 |
| 视觉理解（照片识别） | 需要多模态模型和图像处理库，复杂度高 |
| 模型对比报告 | 需要运行多个模型，耗时较长，Level4内容 |
| Uncensored模型 | 涉及安全考量，本轮不做 |

### 3.3 代码产物 vs 手动截图

| 类型 | 内容 | 状态 |
|------|------|------|
| **代码产物** | Python源代码（4个文件） | ✅ 已完成 |
| **代码产物** | requirements.txt | ✅ 已完成 |
| **代码产物** | map.html（Folium地图） | ✅ 已生成示例 |
| **代码产物** | 8个Markdown文档 | ✅ 已完成 |
| **代码产物** | raw_model_output.log | 运行后自动生成 |
| **手动截图** | Ollama运行界面截图 | 📷 需用户本地截图 |
| **手动截图** | 设备CPU/内存/GPU截图 | 📷 需用户本地截图 |
| **手动填入** | 实际推理速度tok/s | 📋 需从运行日志获取 |
| **手动填入** | 实际模型原始输出 | 📋 需从运行日志粘贴 |

---

## 四、地图数据来源说明

### 4.1 关键声明

> **本项目地点数据完全由本地 Gemma 4 E4B 模型生成，不是手动编写的JSON。**

- 代码通过 Ollama OpenAI 兼容 API（`localhost:11434/v1/chat/completions`）调用本地模型
- 模型根据系统提示词和用户指令，输出 JSON 格式的地点数据
- 代码解析模型输出后，将数据传递给 Folium 渲染地图
- 全过程无任何硬编码地点坐标 JSON

### 4.2 数据流向

```
用户指令 → 系统提示词约束 → Ollama API调用 → Gemma 4模型推理
→ 原始文本输出 → JSON解析（5层容错） → 结构化数据 → Folium地图渲染
```

### 4.3 map.html 说明

项目中的 `卢怡然_C4D_map.html` 是使用演示数据生成的示例地图。

- **演示模式**：运行 `python map_generator.py` 使用演示数据生成地图
- **正式模式**：运行 `python sias_agent.py` 由本地模型生成数据后渲染地图

> 正式提交时，请运行 `python sias_agent.py` 让模型生成数据后重新生成的 map.html 为准。

---

## 五、版权与许可

| 项目 | 许可 |
|------|------|
| 本项目代码 | 学生作业，引用请注明出处 |
| Gemma 4 模型 | Apache 2.0 开源协议 |
| Ollama | MIT 协议 |
| Folium | MIT 协议 |
| Leaflet.js | BSD-2-Clause 协议 |
| OpenStreetMap 瓦片 | CC-BY-SA 2.0 |

---

## 六、联系与致谢

- 学生：卢怡然
- 专业：大数据应用开发
- 课程：Challenge C4D
- AI辅助工具：TRAE

> 本项目使用 TRAE AI 工具辅助完成代码编写和文档撰写，所有AI对话记录见 `卢怡然_C4D_AI日志.md`。
