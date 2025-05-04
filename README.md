# kevin_AI-bug-fixed-
#Model Interaction Interface

Model Interaction Interface 是一个基于 Python 的图形用户界面应用程序，旨在为用户提供一个便捷的平台与多种 AI 模型进行交互。该应用使用 Tkinter 构建 GUI，借助 OpenAI 库调用不同的 AI 模型。用户可以轻松地选择模型、输入问题，并实时查看模型的回答。同时，程序提供了一系列实用功能，如令牌管理、上下文管理、模型切换等，以提升用户的使用体验。

功能特性
多模型支持
程序支持多种 AI 模型，包括普通模型和备用模型。普通模型通常是一些免费但有使用限制的模型，而备用模型则在普通模型达到使用限制时提供支持。用户可以通过下拉菜单方便地选择不同的模型。

令牌管理
程序会对令牌的使用进行实时跟踪和管理。用户有一定数量的令牌可用，每次请求模型回答都会消耗相应的令牌。当令牌不足时，程序会提示用户并自动退出。

上下文管理
用户可以设置上下文消息的数量，包括无上下文、固定数量上下文和无限上下文。这有助于模型更好地理解用户的问题，特别是在多轮对话场景下。

背景颜色设置
程序提供了多种背景颜色供用户选择，用户可以根据自己的喜好在设置界面中更改应用的背景颜色，提升视觉体验。

模型切换机制
当普通模型达到每日使用次数限制时，程序会自动切换到备用模型，并更新模型选择下拉菜单，确保用户可以继续使用应用。

历史记录保存
程序会定期将会话历史记录保存到 cache.json 文件中，下次启动程序时会自动加载之前的会话，方便用户继续对话。

技术栈
Python：作为主要的编程语言，用于实现程序的核心逻辑和业务功能。
Tkinter：Python 的标准 GUI 库，用于构建用户界面，提供了丰富的组件和布局管理器。
OpenAI：用于与 AI 模型进行交互，发送请求并接收模型的响应。
datetime：用于处理日期和时间，记录请求时间和当前日期。
threading：用于实现多线程，避免在进行模型请求时界面出现卡顿。
json：用于处理 JSON 数据，保存和加载会话历史记录。
re：用于正则表达式匹配，在令牌计算中对中文和英文进行分词处理。
安装与配置
环境要求
Python 3.9 及以上版本。你可以从 Python 官方网站 下载并安装最新版本的 Python。
依赖安装
在命令行中使用以下命令安装所需的 Python 库：


bash
pip install openai
API 密钥配置
在代码中，你需要配置普通模型和备用模型的 API 密钥和基础 URL。在代码中找到以下部分并进行修改：


en.py
Apply
# 普通 API 配置
original_api_key = "your_original_api_key"
original_base_url = "https://your_original_base_url/"

# 备用 API 配置
backup_api_key = "your_backup_api_key"
backup_base_url = "https://your_backup_base_url/"
请将 your_original_api_key、https://your_original_base_url/、your_backup_api_key 和 https://your_backup_base_url/ 替换为你实际的 API 密钥和基础 URL。

使用指南
启动程序
下载代码后，在命令行中导航到代码所在目录，运行以下命令启动程序：


bash
python c:/Users/sayhi/Desktop/FAQ（newest）/en.py
模型选择
程序启动后，在界面的顶部会有一个模型选择下拉菜单。你可以从下拉菜单中选择要使用的模型，然后点击“Select”按钮确认选择。选择模型后，程序会弹出提示框显示所选的模型名称。

提问与交互
在界面的底部有一个输入框，你可以在输入框中输入要询问的问题。输入完成后，点击“Send”按钮或按下回车键发送问题。模型的回答会显示在上方的文本区域中，回答会逐字显示，并且支持对加粗文本和代码块的格式处理。

设置功能
点击界面上的“Settings”按钮，会弹出设置窗口。在设置窗口中，你可以进行以下操作：

背景颜色设置：通过下拉菜单选择不同的背景颜色，点击确认后界面的背景颜色会相应改变。
提示词设置：在输入框中输入新的提示词，点击“Save Prompt”按钮保存提示词。提示词会影响模型的回答风格。
上下文消息数量设置：通过下拉菜单选择上下文消息的数量，包括无上下文、固定数量上下文和无限上下文。
查看模型帮助：点击“View Model Help”按钮，会弹出窗口显示模型的对应信息和用户协议。
代码结构与核心模块
模块导入与全局变量
代码开头导入了所需的模块，包括 Tkinter、OpenAI 等。同时定义了一系列全局变量，如请求次数记录、令牌限制、模型配置等。这些全局变量在整个程序中共享使用。


en.py
Apply
import tkinter as tk
from tkinter import scrolledtext, messagebox
from openai import OpenAI
from datetime import datetime
import threading
import time
import re
import json
import os

request_times = []
MAX_REQUESTS_IN_10_SECONDS = 2
today = datetime.now().strftime("%Y-%m-%d")
model_prompts = {
    # 模型提示词配置
}
tokens_limit = 1000000
tokens_used = 0
# 其他全局变量...
令牌管理模块
令牌管理模块包含了检查令牌、扣除令牌和计算令牌的函数。


en.py
Apply
def check_tokens(tokens_used, tokens_needed):
    if tokens_used + tokens_needed > tokens_limit:
        messagebox.showwarning("Insufficient Tokens", "Insufficient tokens. Unable to continue the conversation.")
        root.destroy()
        return False
    return True

def deduct_tokens(tokens_used, tokens_needed):
    tokens_used += tokens_needed
    return tokens_used

def count_tokens(text):
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    chinese_token_count = len(chinese_chars) * 30
    english_words = re.findall(r'\b\w+\b', text)
    english_token_count = len(english_words) * 20
    return chinese_token_count + english_token_count
check_tokens 函数用于检查剩余令牌是否足够，deduct_tokens 函数用于扣除使用的令牌，count_tokens 函数根据文本内容计算所需的令牌数量。

模型请求与响应模块
该模块的核心函数是 create_completion，用于向模型发送请求并处理响应。


en.py
Apply
def create_completion(user_input, tokens_used, conversation, output_text):
    global is_responding, models, api_key, base_url, client, model, model_menu
    is_responding = True
    send_button.config(state=tk.DISABLED)
    # 构造请求 payload
    payload = {
        "messages": conversation + [
            {
                "role": "user",
                "content": user_input
            }
        ]
    }
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=payload["messages"],
            stream=True
        )
        # 处理流式响应
        for chunk in completion:
            # 处理响应内容
            pass
    except Exception as e:
        # 处理异常，如切换模型
        pass
    # 处理响应结束后的操作
    pass
该函数会构造请求的 payload，使用 OpenAI 库发送请求，并处理流式响应。如果请求过程中出现异常，如达到模型使用限制，会自动切换到备用模型。

用户界面模块
使用 Tkinter 构建用户界面，包括模型选择下拉菜单、输入框、发送按钮、输出文本区域等组件。


en.py
Apply
root = tk.Tk()
root.title("Model Interaction Interface - Powered by Kevin")
# 配置界面背景等属性
model_frame = tk.Frame(root, bg=light_bg_colors[0])
model_frame.pack(pady=5, fill=tk.X)

model_label = tk.Label(model_frame, text="Select Model:", bg=light_bg_colors[0])
model_label.pack(side=tk.LEFT, padx=5)

model_var = tk.StringVar(root)
model_var.set("qwen3")
model_menu = tk.OptionMenu(model_frame, model_var, *original_models.keys(), command=lambda _: select_model())
model_menu.pack(side=tk.LEFT, padx=5)

# 其他界面组件...
历史记录管理模块
该模块负责定期保存会话历史记录到 cache.json 文件，并在程序启动时加载之前的会话。


en.py
Apply
def save_history():
    data = {
        "conversation": conversation,
        "tokens_used": tokens_used,
        "output_text": output_text.get("1.0", tk.END)
    }
    with open("cache.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    root.after(2000, save_history)

if os.path.exists("cache.json"):
    with open("cache.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        conversation = data["conversation"]
        tokens_used = data["tokens_used"]
        output_text.config(state=tk.NORMAL)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, data["output_text"])
        output_text.config(state=tk.DISABLED)
        token_label.config(text=f"Tokens consumed: {tokens_used}, Remaining tokens: {tokens_limit - tokens_used}")
高级功能详解
模型切换机制
当普通模型达到每日使用次数限制时，程序会捕获相应的异常，并自动切换到备用模型。切换过程包括更新 API 配置、更新模型选择下拉菜单的选项，并重新发起请求。


en.py
Apply
if "Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day" in error_msg:
    messagebox.showinfo("Model Limit Exceeded", "模型次数用尽，明天再来，即将为您切换到普通线路。")
    # 切换到备用配置
    models = backup_models
    api_key = backup_api_key
    base_url = backup_base_url
    client = OpenAI(base_url=base_url, api_key=api_key)
    # 更新 OptionMenu 的选项
    menu = model_menu["menu"]
    menu.delete(0, "end")
    for key in models.keys():
        menu.add_command(label=key, command=lambda value=key: model_var.set(value))
    # 设置默认选中第一个选项
    if models:
        first_key = next(iter(models))
        model_var.set(first_key)
        model = models[first_key]
    messagebox.showinfo("Configuration Changed", "Switched to backup model provider.")
    # 重新尝试请求
    return create_completion(user_input, tokens_used, conversation, output_text)
上下文管理
用户可以在设置界面中选择上下文消息的数量。在发送请求时，程序会根据用户的选择构造有效的对话上下文。


en.py
Apply
def send_question(event=None):
    # ...
    def run_conversation():
        if context_count == "None":
            effective_conversation = [conversation[0]]
        elif context_count == "Unlimited":
            effective_conversation = conversation
        else:
            try:
                count = int(context_count)
                effective_conversation = [conversation[0]] + conversation[-2 * count:]
            except ValueError:
                effective_conversation = conversation
        completion, tokens_needed = create_completion(user_input, tokens_used, effective_conversation, output_text)
        # ...
请求频率限制
程序会记录每次请求的时间，并检查在 15 秒内的请求次数是否超过限制。如果超过限制，会弹出错误提示框并阻止用户继续发送请求。


en.py
Apply
def check_request_limit():
    global request_times
    now = time.time()
    request_times = [t for t in request_times if now - t < 15]
    if len(request_times) >= MAX_REQUESTS_IN_10_SECONDS:
        messagebox.showerror("Server Error", "Server error. Please try again later.")
        return False
    request_times.append(now)
    return True
常见问题与解决方案
API 调用报错
错误信息：Rate limit exceeded: free-models-per-day

原因：普通模型达到每日使用次数限制。

解决方案：程序会自动切换到备用模型，用户可以继续使用。如果备用模型也有问题，请检查备用 API 密钥和基础 URL 是否正确。

错误信息：KeyError

原因：模型字典中不存在对应的键，可能是模型选择错误或代码中模型配置有误。

解决方案：检查 original_models 和 backup_models 字典，确保模型键的正确性。

界面无响应
原因：模型请求过程中，由于网络延迟或模型处理时间过长，可能导致界面无响应。
解决方案：程序使用了多线程处理模型请求，一般不会出现界面卡顿。如果仍然出现无响应的情况，可以检查网络连接，或者尝试减少请求的频率。
令牌计算不准确
原因：令牌计算规则可能不适用于某些特殊字符或文本格式。
解决方案：可以修改 count_tokens 函数，调整中文和英文的分词规则，以提高令牌计算的准确性。
扩展与定制
添加新模型
要添加新的模型，需要在 original_models 或 backup_models 字典中添加新的模型配置。同时，在 model_prompts 字典中添加对应的模型提示词。


en.py
Apply
# 添加新的普通模型
original_models = {
    # 原有模型配置
    "new_model": "new_model_api_identifier"
}

# 添加新的模型提示词
model_prompts = {
    # 原有提示词配置
    "new_model_api_identifier": "This is the prompt for the new model."
}
修改界面样式
可以通过修改 Tkinter 组件的属性来改变界面的样式，如背景颜色、字体、按钮大小等。例如，修改界面的背景颜色：


en.py
Apply
light_bg_colors = ["#FF0000", "#00FF00", "#0000FF"]  # 修改背景颜色列表
root.configure(bg=light_bg_colors[0])
自定义令牌计算规则
可以修改 count_tokens 函数，根据自己的需求调整中文和英文的分词规则。例如，增加对数字的令牌计算：


en.py
Apply
def count_tokens(text):
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    chinese_token_count = len(chinese_chars) * 30
    english_words = re.findall(r'\b\w+\b', text)
    english_token_count = len(english_words) * 20
    numbers = re.findall(r'\d+', text)
    number_token_count = len(''.join(numbers)) * 10
    return chinese_token_count + english_token_count + number_token_count
贡献指南
如果你对本项目感兴趣，欢迎贡献代码或提出改进建议。可以按照以下步骤进行贡献：

Fork 本项目到自己的 GitHub 仓库。
创建一个新的分支，进行代码修改或功能添加。
提交代码并创建 Pull Request。
等待项目维护者审核并合并代码。
在提交代码时，请确保代码符合 PEP 8 编码规范，并添加必要的注释和文档。

许可证
本项目采用 MIT 许可证。你可以自由使用、修改和分发本项目的代码，但需要保留许可证声明。
