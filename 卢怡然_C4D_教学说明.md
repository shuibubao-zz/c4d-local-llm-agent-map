# 卢怡然_C4D_教学说明（复现文档）

> 本文档一步一步教你如何从零开始复现本项目全部效果。
> 适合任何人按照步骤操作即可完成。
> 学生：卢怡然 | 日期：2026年10月

---

## 前置条件

| 条件 | 要求 |
|------|------|
| 操作系统 | Windows 10/11（Mac/Linux也可，命令略有不同） |
| 内存 | ≥8GB（推荐16GB） |
| 硬盘空间 | ≥10GB（模型文件约5GB） |
| Python版本 | ≥3.8 |
| 网络 | 安装时需要联网下载模型和依赖 |

---

## Step 1：安装 Ollama

### 1.1 下载安装

**Windows：**
1. 访问 https://ollama.com/download
2. 下载 Windows 版安装包（OllamaSetup.exe）
3. 双击运行，按提示安装完成
4. 安装完成后 Ollama 会自动启动（可在系统托盘看到图标）

**Mac：**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux：**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 1.2 验证安装

打开终端（Windows用PowerShell），运行：
```bash
ollama --version
```
看到版本号输出即安装成功。

### 1.3 启动 Ollama 服务

```bash
ollama serve
```
> 如果 Ollama 已在后台运行（系统托盘有图标），则此步骤可跳过。
> 服务默认运行在 `http://localhost:11434`

---

## Step 2：拉取 Gemma 4 E4B 模型

### 2.1 拉取模型

```bash
ollama pull gemma4:e4b
```

> 首次拉取需要下载约 3-5GB 模型文件，请耐心等待。
> 下载速度取决于你的网络环境。

### 2.2 验证模型已安装

```bash
ollama list
```
应该能看到 `gemma4:e4b` 在列表中。

### 2.3 测试模型运行

```bash
ollama run gemma4:e4b "你好，请用一句话介绍你自己"
```
如果模型正常回复文字，说明模型已就绪。

### 2.4 验证 API 接口可用

```bash
# Windows PowerShell
Invoke-RestMethod -Uri "http://localhost:11434/v1/chat/completions" -Method Post -ContentType "application/json" -Body '{"model":"gemma4:e4b","messages":[{"role":"user","content":"说hello"}]}'

# 或用 curl（如果已安装）
curl http://localhost:11434/v1/chat/completions -H "Content-Type: application/json" -d "{\"model\":\"gemma4:e4b\",\"messages\":[{\"role\":\"user\",\"content\":\"说hello\"}]}"
```

如果返回 JSON 格式的响应（包含模型回复），说明 API 接口正常。

---

## Step 3：安装 Python 环境

### 3.1 安装 Python

如果尚未安装 Python：
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.10+（推荐3.11或3.12）
3. 安装时**勾选 "Add Python to PATH"**
4. 验证：`python --version`

### 3.2 安装项目依赖

进入项目 `agent-skill` 目录：
```bash
cd "C:\Users\你的用户名\Desktop\卢怡然_C4D\卢怡然_C4D_agent-skill"
```

安装依赖：
```bash
pip install -r requirements.txt
```

这会安装两个核心依赖：
- `requests`：用于调用 Ollama API
- `folium`：用于生成交互式地图

### 3.3 验证依赖安装

```bash
python -c "import requests; import folium; print('依赖安装成功！')"
```

---

## Step 4：运行 Agent 生成地图

### 4.1 运行主程序

确保 Ollama 服务正在运行（系统托盘有图标或 `ollama serve` 在后台），然后执行：

```bash
cd "C:\Users\你的用户名\Desktop\卢怡然_C4D\卢怡然_C4D_agent-skill"
python sias_agent.py
```

### 4.2 预期输出

程序运行后会显示类似以下输出：

```
============================================================
SIAS University 本地 LLM Agent
模型: Gemma 4 E4B Q4_K_M
API: http://localhost:11434/v1/chat/completions
============================================================

[1/4] 正在向本地模型发送指令...
用户指令: 给我生成一个 SIAS University（郑州西亚斯学院）周边的地图...

[2/4] 模型响应完成！
  推理耗时: XX.XX 秒
  输出 Token: XXXX
  推理速度: XX.XX tok/s

[3/4] 解析模型输出的 JSON 数据...
  JSON 解析成功（直接解析）
  第 1 个地点验证通过: 西亚斯学院正门 (34.4065, 113.7382)
  第 2 个地点验证通过: 西亚斯图书馆 (34.4055, 113.7395)
  ...
  成功解析 8 个地点！

[4/4] 生成交互式地图...
  [添加] 1. 西亚斯学院正门 (SIAS University Main Gate) - (34.4065, 113.7382)
  [添加] 2. 西亚斯图书馆 (SIAS University Library) - (34.4055, 113.7395)
  ...

地图已生成: 卢怡然_C4D_map.html
共标记 8 个地点 + 1 个中心点（SIAS University）
请在浏览器中打开 卢怡然_C4D_map.html 查看交互式地图。
```

### 4.3 Level3：多轮对话模式

程序运行完成后，会进入多轮对话模式：

```
============================================================
【Level3 功能】多轮对话模式已启用
你可以：
  1. 输入 'add 地点名称' 新增标记点
  2. 输入 'modify 旧名称 新描述' 修改标记点
  3. 输入 'quit' 退出并重新生成地图
============================================================

请输入指令: add 新郑火车站
```

- 输入 `add 新郑火车站` → Agent 调用模型生成该地点数据并添加到地图
- 输入 `modify 西亚斯食堂 新的描述文字` → 修改已有标记点信息
- 输入 `quit` → 退出程序，地图和日志已自动保存

---

## Step 5：查看生成的地图

### 5.1 打开地图

地图文件生成在项目根目录：
```
卢怡然_C4D\卢怡然_C4D_map.html
```

直接双击此文件，会用默认浏览器打开交互式地图。

### 5.2 地图功能体验

| 操作 | 效果 |
|------|------|
| 鼠标滚轮 | 缩放地图 |
| 鼠标拖拽 | 平移地图 |
| 点击标记点 | 弹出弹窗，显示地点详细信息 |
| 左上角按钮 | 全屏模式 |
| 右上角按钮 | 测距工具 |
| 右下角图层 | 切换底图类型（标准/地形/黑白） |
| 底部 | 显示鼠标坐标和比例尺 |

---

## Step 6：查看日志文件

运行后会产生以下日志文件：

| 文件 | 位置 | 内容 |
|------|------|------|
| `raw_model_output.log` | `agent-skill/` 目录 | 模型原始输出完整记录 |
| `卢怡然_C4D_AI日志.md` | 项目根目录 | 格式化的AI对话日志 |

将日志内容复制到 `卢怡然_C4D_AI日志.md` 的对应位置。

---

## 常见问题排查

### Q1：连接失败 "无法连接到 localhost:11434"

**原因：** Ollama 服务未启动。

**解决：**
```bash
ollama serve
```
或检查系统托盘是否有 Ollama 图标，如果没有，从开始菜单启动 Ollama。

### Q2：模型未找到 "model not found"

**原因：** 未拉取 gemma4:e4b 模型。

**解决：**
```bash
ollama pull gemma4:e4b
```

### Q3：JSON 解析失败

**原因：** 模型输出格式不稳定。

**解决：** 代码已内置5层容错策略。如果仍然失败：
1. 降低 temperature（在 config.py 中修改为 0.1）
2. 增大 max_tokens（改为 8192）
3. 优化系统提示词
4. 多运行几次（本地模型输出有随机性）

### Q4：地图无法显示

**原因：** Folium 未正确安装，或网络问题导致瓦片加载失败。

**解决：**
```bash
pip install folium --upgrade
```
地图瓦片来自 OpenStreetMap，需要网络连接。如果地图框架显示但瓦片空白，检查网络。

### Q5：pip install 失败

**解决：** 尝试使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q6：运行速度太慢

**原因：** 本地推理速度取决于设备性能，16GB内存笔记本约 5-20 tok/s。

**解决：**
1. 确认没有其他大型程序占用内存
2. 如果有独立显卡，配置 Ollama 使用 GPU 加速
3. 降低 max_tokens 参数

---

## 完整复现清单

复现本项目需要完成以下步骤：

- [ ] 1. 安装 Ollama
- [ ] 2. 拉取 gemma4:e4b 模型
- [ ] 3. 安装 Python 3.10+
- [ ] 4. 安装依赖 (pip install -r requirements.txt)
- [ ] 5. 运行 python sias_agent.py
- [ ] 6. 查看生成的 map.html 地图
- [ ] 7. 体验 Level3 多轮对话功能
- [ ] 8. 查看日志文件
- [ ] 9. 截图补充（Ollama界面、设备信息、地图效果）

按照以上步骤操作，任何人都可以完整复现本项目效果。
