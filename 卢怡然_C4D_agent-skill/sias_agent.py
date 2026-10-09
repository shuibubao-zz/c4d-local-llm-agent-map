# -*- coding: utf-8 -*-
"""
SIAS University 本地 LLM Agent
================================
核心 Agent 模块：负责与本地 Gemma 4 模型交互，获取结构化地点数据。

工作流程：
1. 构建系统提示词 + 用户指令
2. 调用 Ollama OpenAI 兼容 API（localhost:11434）
3. 解析模型返回的 JSON（含容错处理）
4. 记录完整对话日志

作者：卢怡然
日期：2026-10
"""

import json
import re
import time
import requests
from datetime import datetime

import config


class SiasAgent:
    """
    SIAS University 本地 LLM Agent 类。

    封装与本地 Gemma 4 模型的所有交互逻辑，包括：
    - 发送请求到 Ollama API
    - 解析模型输出的 JSON
    - JSON 解析失败的容错处理
    - 完整对话日志记录
    - Level3：多轮对话支持（新增/修改标记点）
    """

    def __init__(self):
        """初始化 Agent，设置对话历史和日志"""
        self.api_url = config.OLLAMA_API_URL
        self.model_name = config.MODEL_NAME
        self.temperature = config.TEMPERATURE
        self.max_tokens = config.MAX_TOKENS
        self.timeout = config.REQUEST_TIMEOUT

        # 对话历史（用于多轮对话，Level3 功能）
        self.conversation_history = []

        # 日志记录列表
        self.log_entries = []

        # 初始化系统提示词到对话历史
        self.conversation_history.append({
            "role": "system",
            "content": config.SYSTEM_PROMPT
        })

    # ============================================================
    # 核心方法：调用本地模型
    # ============================================================

    def call_model(self, user_message):
        """
        调用本地 Gemma 4 模型，发送用户消息并获取响应。

        参数：
            user_message (str): 用户输入的指令

        返回：
            str: 模型返回的原始文本内容
        """
        # 将用户消息加入对话历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # 构建请求体（Ollama OpenAI 兼容格式）
        request_body = {
            "model": self.model_name,
            "messages": self.conversation_history,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False  # 非流式输出，便于一次性获取完整响应
        }

        # 记录请求日志
        request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_entry("========== 请求发送 ==========")
        self._log_entry(f"时间: {request_time}")
        self._log_entry(f"模型: {self.model_name}")
        self._log_entry(f"API地址: {self.api_url}")
        self._log_entry(f"用户指令: {user_message}")
        self._log_entry(f"请求参数: temperature={self.temperature}, max_tokens={self.max_tokens}")

        # 记录推理开始时间（用于计算 tok/s）
        start_time = time.time()

        try:
            # 发送 POST 请求到 Ollama 本地 API
            response = requests.post(
                self.api_url,
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )

            # 检查 HTTP 状态码
            response.raise_for_status()

        except requests.exceptions.ConnectionError:
            # 连接失败：Ollama 服务未启动
            error_msg = (
                f"[连接失败] 无法连接到 {self.api_url}。\n"
                f"请确认 Ollama 服务已启动（运行命令：ollama serve）。\n"
                f"请确认已拉取模型（运行命令：ollama pull {self.model_name}）。"
            )
            self._log_entry(f"错误: {error_msg}")
            raise ConnectionError(error_msg)

        except requests.exceptions.Timeout:
            # 请求超时
            error_msg = f"[请求超时] 模型推理超过 {self.timeout} 秒，请检查设备性能或增大超时时间。"
            self._log_entry(f"错误: {error_msg}")
            raise TimeoutError(error_msg)

        except requests.exceptions.HTTPError as e:
            # HTTP 错误（如 404 模型不存在、500 内部错误）
            error_msg = f"[HTTP错误] 状态码 {response.status_code}，错误信息: {response.text}"
            self._log_entry(f"错误: {error_msg}")
            raise Exception(error_msg)

        # 计算推理耗时
        elapsed_time = time.time() - start_time

        # 解析响应
        response_data = response.json()

        # 提取模型输出内容
        model_output = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

        # 提取 token 使用量（用于计算 tok/s）
        usage = response_data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        # 计算推理速度（tok/s）
        if elapsed_time > 0 and completion_tokens > 0:
            tokens_per_second = completion_tokens / elapsed_time
        else:
            tokens_per_second = 0

        # 记录响应日志
        self._log_entry("========== 模型响应 ==========")
        self._log_entry(f"响应时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log_entry(f"推理耗时: {elapsed_time:.2f} 秒")
        self._log_entry(f"Token 统计: 输入={prompt_tokens}, 输出={completion_tokens}, 总计={total_tokens}")
        self._log_entry(f"推理速度: {tokens_per_second:.2f} tok/s")
        self._log_entry(f"模型原始输出:\n{model_output}")
        self._log_entry("=" * 60)

        # 将模型回复加入对话历史（用于多轮对话）
        self.conversation_history.append({
            "role": "assistant",
            "content": model_output
        })

        return model_output, {
            "elapsed_time": elapsed_time,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "tokens_per_second": tokens_per_second
        }

    # ============================================================
    # JSON 解析与容错处理（关键 Agent 能力）
    # ============================================================

    def parse_json_response(self, model_output):
        """
        解析模型输出的 JSON 数据，包含多层容错处理。

        容错策略：
        1. 直接 json.loads 解析
        2. 如果失败，提取 JSON 数组部分（正则匹配 [ 到 ] 之间内容）
        3. 如果失败，提取 JSON 对象部分（正则匹配 { 到 } 之间内容）
        4. 如果失败，清理 markdown 代码块标记后重试
        5. 如果仍然失败，返回 None 并记录错误日志

        参数：
            model_output (str): 模型返回的原始文本

        返回：
            list 或 dict: 解析后的 JSON 数据，失败返回 None
        """
        self._log_entry("========== JSON 解析过程 ==========")

        # 策略1：直接解析
        try:
            data = json.loads(model_output)
            self._log_entry("JSON 解析成功（直接解析）")
            self._validate_location_data(data)
            return data
        except json.JSONDecodeError as e:
            self._log_entry(f"直接解析失败: {e}，尝试容错策略...")

        # 策略2：提取 JSON 数组（[ ... ]）
        try:
            json_array_match = re.search(r'\[.*\]', model_output, re.DOTALL)
            if json_array_match:
                data = json.loads(json_array_match.group())
                self._log_entry("JSON 解析成功（正则提取数组）")
                self._validate_location_data(data)
                return data
        except (json.JSONDecodeError, AttributeError) as e:
            self._log_entry(f"正则提取数组失败: {e}，继续尝试...")

        # 策略3：提取 JSON 对象（{ ... }）
        try:
            json_object_match = re.search(r'\{.*\}', model_output, re.DOTALL)
            if json_object_match:
                data = json.loads(json_object_match.group())
                self._log_entry("JSON 解析成功（正则提取对象）")
                return data
        except (json.JSONDecodeError, AttributeError) as e:
            self._log_entry(f"正则提取对象失败: {e}，继续尝试...")

        # 策略4：清理 markdown 代码块标记后重试
        try:
            cleaned = model_output
            cleaned = re.sub(r'```json\s*', '', cleaned)  # 移除 ```json
            cleaned = re.sub(r'```\s*', '', cleaned)       # 移除 ```
            cleaned = cleaned.strip()
            data = json.loads(cleaned)
            self._log_entry("JSON 解析成功（清理 markdown 标记后解析）")
            self._validate_location_data(data)
            return data
        except json.JSONDecodeError as e:
            self._log_entry(f"清理后解析失败: {e}")

        # 策略5：逐行清理后尝试构建
        try:
            lines = model_output.strip().split('\n')
            json_lines = [line for line in lines if not line.strip().startswith('#')]
            cleaned = '\n'.join(json_lines).strip()
            json_array_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if json_array_match:
                data = json.loads(json_array_match.group())
                self._log_entry("JSON 解析成功（逐行清理后提取）")
                self._validate_location_data(data)
                return data
        except (json.JSONDecodeError, AttributeError) as e:
            self._log_entry(f"逐行清理后解析失败: {e}")

        # 所有策略均失败
        self._log_entry("【警告】所有 JSON 解析策略均失败！返回 None")
        self._log_entry(f"原始输出内容:\n{model_output}")
        return None

    def _validate_location_data(self, data):
        """
        验证地点数据格式是否完整。

        检查每个地点是否包含必需字段：
        name, name_zh, latitude, longitude, description

        参数：
            data: 解析后的 JSON 数据（列表或字典）

        异常：
            如果字段缺失，记录警告日志但不中断程序
        """
        # 确保是列表格式
        locations = data if isinstance(data, list) else [data]

        required_fields = ["name", "name_zh", "latitude", "longitude", "description"]

        for i, loc in enumerate(locations):
            missing_fields = [f for f in required_fields if f not in loc]
            if missing_fields:
                self._log_entry(
                    f"【警告】第 {i+1} 个地点缺少字段: {', '.join(missing_fields)}"
                )
            else:
                self._log_entry(
                    f"第 {i+1} 个地点验证通过: {loc.get('name_zh', '未知')} "
                    f"({loc.get('latitude', 0)}, {loc.get('longitude', 0)})"
                )

    # ============================================================
    # Level3 扩展：多轮对话功能
    # ============================================================

    def add_marker(self, location_name):
        """
        多轮对话：新增一个地图标记点。

        用户可以输入一个地点名称，Agent 会调用模型生成该地点的结构化数据，
        然后添加到已有地点列表中。

        参数：
            location_name (str): 用户想要新增的地点名称

        返回：
            dict: 新增地点的 JSON 对象，失败返回 None
        """
        prompt = config.ADD_MARKER_PROMPT_TEMPLATE.format(location_name=location_name)
        model_output, metrics = self.call_model(prompt)
        new_location = self.parse_json_response(model_output)

        if new_location and isinstance(new_location, dict):
            self._log_entry(f"新增标记点成功: {new_location.get('name_zh', location_name)}")
            return new_location
        elif new_location and isinstance(new_location, list) and len(new_location) > 0:
            self._log_entry(f"新增标记点成功: {new_location[0].get('name_zh', location_name)}")
            return new_location[0]
        else:
            self._log_entry(f"新增标记点失败: 无法解析模型输出")
            return None

    def modify_marker(self, old_name, new_info):
        """
        多轮对话：修改已有地图标记点信息。

        参数：
            old_name (str): 需要修改的地点名称
            new_info (str): 新的地点信息描述

        返回：
            dict: 修改后的地点 JSON 对象，失败返回 None
        """
        prompt = config.MODIFY_MARKER_PROMPT_TEMPLATE.format(
            old_name=old_name, new_info=new_info
        )
        model_output, metrics = self.call_model(prompt)
        modified_location = self.parse_json_response(model_output)

        if modified_location:
            self._log_entry(f"修改标记点成功: {old_name} -> {new_info}")
            return modified_location
        else:
            self._log_entry(f"修改标记点失败: 无法解析模型输出")
            return None

    # ============================================================
    # Level3 扩展预留：多工具调用接口
    # ============================================================

    def call_tool(self, tool_name, **kwargs):
        """
        多工具调用接口（预留扩展）。

        当前版本未实现具体工具逻辑，仅提供接口框架。
        未来可接入以下工具：
        - weather_query: 查询指定地点天气
        - route_planning: 规划两地点间路线
        - rating_query: 查询地点评分
        - image_recognition: 识别照片中建筑

        参数：
            tool_name (str): 工具名称
            **kwargs: 工具参数

        返回：
            dict: 工具调用结果
        """
        # TODO: 实现具体工具调用逻辑
        # 示例：
        # if tool_name == "weather_query":
        #     return self._query_weather(kwargs.get("location"))
        # elif tool_name == "route_planning":
        #     return self._plan_route(kwargs.get("start"), kwargs.get("end"))

        self._log_entry(f"[预留接口] 工具 '{tool_name}' 尚未实现，参数: {kwargs}")
        return {"status": "not_implemented", "tool": tool_name}

    # ============================================================
    # 日志记录方法
    # ============================================================

    def _log_entry(self, message):
        """
        记录一条日志到内存列表和原始输出文件。

        参数：
            message (str): 日志内容
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        self.log_entries.append(log_line)

        # 同时写入原始输出日志文件
        try:
            with open(config.RAW_OUTPUT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception:
            pass  # 日志写入失败不影响主流程

    def get_logs(self):
        """
        获取完整对话日志。

        返回：
            str: 格式化的完整日志文本
        """
        return "\n".join(self.log_entries)

    def save_logs_to_markdown(self, file_path=None):
        """
        将对话日志保存为 Markdown 格式文件（用于 AI日志文档）。

        参数：
            file_path (str): 输出文件路径，默认使用配置文件中的路径
        """
        if file_path is None:
            file_path = config.AI_LOG_FILE

        markdown_content = self._generate_ai_log_markdown()

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"AI 日志已保存至: {file_path}")
        except Exception as e:
            print(f"AI 日志保存失败: {e}")

    def _generate_ai_log_markdown(self):
        """
        生成 AI 日志的 Markdown 内容。

        返回：
            str: Markdown 格式的日志内容
        """
        md = []
        md.append("# 卢怡然_C4D_AI日志\n")
        md.append("> 本文档记录 Agent 每一轮 prompt 输入、模型原始输出内容、JSON 解析过程。\n")
        md.append(f"> 模型: {config.MODEL_FULL_NAME} | 运行工具: Ollama | API: {config.OLLAMA_API_URL}\n")
        md.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append("\n---\n")

        for entry in self.log_entries:
            md.append(f"```\n{entry}\n```\n")

        return "\n".join(md)


# ============================================================
# 主程序入口
# ============================================================

def main():
    """
    主函数：执行完整的 Agent 工作流程。

    流程：
    1. 初始化 Agent
    2. 发送用户指令到本地 Gemma 4 模型
    3. 解析模型返回的 JSON 地点数据
    4. 生成 Folium 交互式地图
    5. 保存对话日志
    6. （Level3）多轮对话：用户可新增/修改标记点
    """
    print("=" * 60)
    print("SIAS University 本地 LLM Agent")
    print(f"模型: {config.MODEL_FULL_NAME}")
    print(f"API: {config.OLLAMA_API_URL}")
    print("=" * 60)

    # 初始化 Agent
    agent = SiasAgent()

    # ---- 第一轮：生成初始地点数据 ----
    print("\n[1/4] 正在向本地模型发送指令...")
    print(f"用户指令: {config.INITIAL_USER_PROMPT[:50]}...")

    try:
        model_output, metrics = agent.call_model(config.INITIAL_USER_PROMPT)

        print(f"\n[2/4] 模型响应完成！")
        print(f"  推理耗时: {metrics['elapsed_time']:.2f} 秒")
        print(f"  输出 Token: {metrics['completion_tokens']}")
        print(f"  推理速度: {metrics['tokens_per_second']:.2f} tok/s")

        # 解析 JSON
        print(f"\n[3/4] 解析模型输出的 JSON 数据...")
        locations = agent.parse_json_response(model_output)

        if locations is None:
            print("【错误】JSON 解析失败，请检查模型输出或调整提示词。")
            print("建议：增大 max_tokens、降低 temperature、优化 system prompt。")
            agent.save_logs_to_markdown()
            return

        if isinstance(locations, dict):
            locations = [locations]

        print(f"  成功解析 {len(locations)} 个地点！")

        # 生成地图
        print(f"\n[4/4] 生成交互式地图...")
        from map_generator import generate_map
        generate_map(locations)

        # 保存日志
        agent.save_logs_to_markdown()
        print(f"\n对话日志已保存。")

        # ---- Level3 扩展：多轮对话 ----
        if config.ENABLE_MULTI_TURN:
            print("\n" + "=" * 60)
            print("【Level3 功能】多轮对话模式已启用")
            print("你可以：")
            print("  1. 输入 'add 地点名称' 新增标记点")
            print("  2. 输入 'modify 旧名称 新描述' 修改标记点")
            print("  3. 输入 'quit' 退出并重新生成地图")
            print("=" * 60)

            while True:
                user_input = input("\n请输入指令: ").strip()

                if user_input.lower() == "quit":
                    # 退出前重新生成包含新增标记点的地图
                    from map_generator import generate_map
                    generate_map(locations)
                    agent.save_logs_to_markdown()
                    print("已重新生成地图并保存日志。退出。")
                    break
                elif user_input.lower().startswith("add "):
                    location_name = user_input[4:].strip()
                    if location_name:
                        new_loc = agent.add_marker(location_name)
                        if new_loc:
                            locations.append(new_loc)
                            print(f"已新增标记点: {new_loc.get('name_zh', location_name)}")
                            from map_generator import generate_map
                            generate_map(locations)
                            print("地图已更新！")
                        else:
                            print("新增标记点失败。")
                elif user_input.lower().startswith("modify "):
                    parts = user_input[7:].strip().split(" ", 1)
                    if len(parts) == 2:
                        old_name, new_info = parts
                        modified = agent.modify_marker(old_name, new_info)
                        if modified:
                            # 更新地点列表中的对应项
                            for i, loc in enumerate(locations):
                                if loc.get("name_zh") == old_name or loc.get("name") == old_name:
                                    locations[i] = modified
                                    break
                            print(f"已修改标记点: {old_name}")
                            from map_generator import generate_map
                            generate_map(locations)
                            print("地图已更新！")
                        else:
                            print("修改标记点失败。")
                    else:
                        print("格式: modify 旧名称 新描述")
                else:
                    print("未知指令。可用: add / modify / quit")

    except ConnectionError as e:
        print(f"\n[连接错误] {e}")
        agent.save_logs_to_markdown()
    except TimeoutError as e:
        print(f"\n[超时错误] {e}")
        agent.save_logs_to_markdown()
    except Exception as e:
        print(f"\n[未知错误] {e}")
        agent.save_logs_to_markdown()


if __name__ == "__main__":
    main()
