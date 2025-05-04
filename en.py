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
    "Qwen/Qwen2.5-7B-Instruct": "",
    "Qwen/Qwen3-8B": "",
    "THUDM/GLM-Z1-9B-0414": "",
    "THUDM/GLM-4-9B-0414": "",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B": "",
    "qwen/qwen3-30b-a3b:free": "",
    "qwen/qwen-2.5-coder-32b-instruct:free": "",
    "qwen/qwen3-235b-a22b:free": "",
    "qwen/qwq-32b:free": "",
    "open-r1/olympiccoder-32b:free": "",
    "deepseek/deepseek-chat-v3-0324:free": "",
    "google/gemma-3-12b-it:free": "",
    "thudm/glm-4-32b:free": "",
    "mistralai/mistral-small-3.1-24b-instruct:free": ""
}

tokens_limit = 1000000
tokens_used = 0
gifts = {}
client = None
is_responding = False
stop_event = threading.Event()

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

# 定义原始和备用模型配置
original_models = {
    "qwen3": "qwen/qwen3-30b-a3b:free",
    "qwen2.5_coder": "qwen/qwen-2.5-coder-32b-instruct:free",
    "qwen3-235b-a22b": "qwen/qwen3-235b-a22b:free",
    "qwq-32b-preview": "qwen/qwq-32b:free",
    "olympiccoder-32b": "open-r1/olympiccoder-32b:free",
    "deepseek_v3": "deepseek/deepseek-chat-v3-0324:free",
    "gemma-3-27b": "google/gemma-3-12b-it:free",
    "glm-4": "thudm/glm-4-32b:free",
    "mistral": "mistralai/mistral-small-3.1-24b-instruct:free"
}
original_api_key = "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"
original_base_url = "https://openrouter.ai/api/v1/"

# 备用配置
backup_models = {
    "Qwen/Qwen2.5": "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen3": "Qwen/Qwen3-8B",
    "THUDM/GLM-Z1-9B-0414": "THUDM/GLM-Z1-9B-0414",
    "THUDM/GLM-4-9B-0414": "THUDM/GLM-4-9B-0414",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
}
backup_api_key = "sk-nfoodijzztqcrgrnhngsqivouoeiashaiqpbjkatyvdvwgmf"
backup_base_url = "https://api.siliconflow.cn/"

# 初始化使用原始配置
models = original_models
api_key = original_api_key
base_url = original_base_url
client = OpenAI(base_url=base_url, api_key=api_key)

# 保存 OptionMenu 实例
model_menu = None

def create_completion(user_input, tokens_used, conversation, output_text):
    global is_responding, models, api_key, base_url, client, model, model_menu
    is_responding = True
    send_button.config(state=tk.DISABLED)
    stop_event.clear()
    payload = {
        "messages": conversation + [
            {
                "role": "user",
                "content": user_input
            }
        ]
    }
    # 禁止鼠标交互
    original_bindtags = output_text.bindtags()
    output_text.bindtags((output_text, root, "all"))
    output_text.config(state=tk.NORMAL)
    input_text.config(state=tk.DISABLED)

    full_response = ""  # 初始化 full_response 变量

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=payload["messages"],
            stream=True
        )
        bold_tag_started = False
        code_block = False
        for chunk in completion:
            if stop_event.is_set():
                # 插入200个杠号
                output_text.insert(tk.END, "\n\n" + "-" * 200 + "\n\n", "gray_line")
                output_text.see(tk.END)
                output_text.update()
                break
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                index = 0
                while index < len(content):
                    if stop_event.is_set():
                        # 插入200个杠号
                        output_text.insert(tk.END, "\n\n" + "-" * 210 + "\n\n", "gray_line")
                        output_text.see(tk.END)
                        output_text.update()
                        break
                    if content[index:index + 3] == "```" and not bold_tag_started:
                        code_block = not code_block
                        index += 3
                    elif content[index:index + 2] == "**" and not code_block:
                        before = content[:index]
                        for char in before:
                            if stop_event.is_set():
                                # 插入200个杠号
                                output_text.insert(tk.END, "\n\n" + "-" * 210 + "\n\n", "gray_line")
                                output_text.see(tk.END)
                                output_text.update()
                                break
                            output_text.insert(tk.END, char, "normal" if not bold_tag_started else "bold")
                            output_text.see(tk.END)
                            output_text.update()
                            time.sleep(0)
                        content = content[index + 2:]
                        index = 0
                        bold_tag_started = not bold_tag_started
                    elif content[index] == "-" and not code_block and not bold_tag_started:
                        before = content[:index]
                        for char in before:
                            if stop_event.is_set():
                                # 插入200个杠号
                                output_text.insert(tk.END, "\n\n" + "-" * 200 + "\n\n", "gray_line")
                                output_text.see(tk.END)
                                output_text.update()
                                break
                            output_text.insert(tk.END, char, "normal")
                            output_text.see(tk.END)
                            output_text.update()
                            time.sleep(0)
                        output_text.insert(tk.END, "·")
                        output_text.see(tk.END)
                        output_text.update()
                        time.sleep(0)
                        content = content[index + 1:]
                        index = 0
                    else:
                        char = content[index]
                        output_text.insert(tk.END, char, "normal" if not bold_tag_started else "bold")
                        output_text.see(tk.END)
                        output_text.update()
                        time.sleep(0)
                        index += 1
    except Exception as e:
        error_msg = str(e)
        if "Rate limit exceeded: free-models-per-day. Add 10 credits to unlock 1000 free model requests per day" in error_msg:
            messagebox.showinfo("Model Limit Exceeded", "模型次数用尽，明天再来，即将为您切换到普通线路。")
            # 切换到备用配置
            models = backup_models
            api_key = backup_api_key
            base_url = backup_base_url
            client = OpenAI(base_url=base_url, api_key=api_key)
            # 重新获取当前模型
            model_choice = model_var.get()
            if model_choice in models:
                model = models[model_choice]
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
        else:
            stop_event.set()
            output_text.insert(tk.END, "\n\n" + "-" * 210 + "\n\n", "gray_line")
            output_text.insert(tk.END, f"Error: {error_msg}\n\n", "error_text")
            output_text.insert(tk.END, "-" * 210 + "\n\n", "gray_line")
            output_text.see(tk.END)
            output_text.update()

    if not stop_event.is_set():
        output_text.insert(tk.END, "\n\n")
        output_text.insert(tk.END, "-" * 210 + "\n\n", "gray_line")
        output_text.see(tk.END)
        output_text.update()
    output_text.config(state=tk.DISABLED)
    input_text.config(state=tk.NORMAL)
    is_responding = False
    send_button.config(state=tk.NORMAL)
    # 恢复鼠标交互
    output_text.bindtags(original_bindtags)
    tokens_needed = count_tokens(full_response)
    return full_response, tokens_needed

def print_completion(completion, tokens_used, tokens_needed, token_label):
    token_label.config(text=f"Tokens consumed: {tokens_needed}, Remaining tokens: {tokens_limit - tokens_used - tokens_needed}")
    tokens_used = deduct_tokens(tokens_used, tokens_needed)
    return tokens_used

def check_request_limit():
    global request_times
    now = time.time()
    request_times = [t for t in request_times if now - t < 15]
    if len(request_times) >= MAX_REQUESTS_IN_10_SECONDS:
        messagebox.showerror("Server Error", "Server error. Please try again later.")
        return False
    request_times.append(now)
    return True

context_count = "Unlimited"

def send_question(event=None):
    global tokens_used, context_count
    if is_responding or not check_request_limit():
        return
    user_input = input_text.get("1.0", tk.END).strip()
    if not user_input:
        messagebox.showwarning("Empty Input", "Input cannot be empty. Please try again.")
        return
    if user_input in gifts:
        tokens_used += gifts[user_input]
        messagebox.showinfo("Gift Code Used", f"Gift code {user_input} has been used. Tokens increased by {gifts[user_input]}.")
        del gifts[user_input]
        input_text.delete("1.0", tk.END)
        return
    user_input += ""
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, f"User: {user_input}\n", "user_input")
    output_text.config(state=tk.DISABLED)
    def run_conversation():
        global tokens_used
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
        if check_tokens(tokens_used, tokens_needed):
            tokens_used = print_completion(completion, tokens_used, tokens_needed, token_label)
            conversation.append({
                "role": "user",
                "content": user_input
            })
            conversation.append({
                "role": "assistant",
                "content": completion
            })
        input_text.delete("1.0", tk.END)
    threading.Thread(target=run_conversation).start()

def select_model():
    global model, conversation
    model_choice = model_var.get()
    if model_choice in models:
        model = models[model_choice]
    else:
        model = "01-ai/Yi-1.5-9B-Chat-16K"
    system_prompt = model_prompts.get(model)
    conversation = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    messagebox.showinfo("Model Selection", f"Selected model: {model}.")

root = tk.Tk()
root.title("Model Interaction Interface - Powered by Kevin")
light_bg_colors = ["#E0FFFF", "#F0FFF0", "#FFFACD", "#FFE4E1", "#FFEBCD", "#F5F5DC", "#FAF0E6", "#FFFAF0", "#FDF5E6", "#FFFFF0", "#F0F8FF", "#E6E6FA", "#FFF0F5", "#FFB6C1", "#FFA07A", "#FFDAB9", "#EEE8AA", "#BDB76B", "#98FB98", "#87CEFA"]
root.configure(bg=light_bg_colors[0])
root.attributes("-topmost", True)
time.sleep(0.5)
root.attributes("-topmost", False)
try:
    root.state('zoomed')
except tk.TclError:
    root.attributes('-fullscreen', True)

model_frame = tk.Frame(root, bg=light_bg_colors[0])
model_frame.pack(pady=5, fill=tk.X)

model_label = tk.Label(model_frame, text="Select Model:", bg=light_bg_colors[0])
model_label.pack(side=tk.LEFT, padx=5)

model_var = tk.StringVar(root)
model_var.set("qwen3")  # 确保这里设置的键存在于 original_models 字典中
model_menu = tk.OptionMenu(model_frame, model_var, *original_models.keys(), command=lambda _: select_model())
model_menu.pack(side=tk.LEFT, padx=5)

select_button = tk.Button(model_frame, text="Select", command=select_model)
select_button.pack(side=tk.LEFT, padx=5)

output_text = scrolledtext.ScrolledText(root, width=100, height=35, state=tk.DISABLED, bg=light_bg_colors[0])
output_text.pack(pady=5, fill=tk.BOTH, expand=True)
default_font = ("SimSun", 11)
bold_font = ("SimSun", 11, "bold")
welcome_font = ("SimSun", 25)
output_text.tag_configure("bold", font=bold_font)
output_text.tag_configure("normal", font=default_font)
output_text.tag_configure("gray_line", foreground="gray")
output_text.tag_configure("welcome", font=welcome_font)
output_text.tag_configure("user_input", foreground="red")
output_text.tag_configure("error_text", foreground="red")

if output_text.get("1.0", tk.END).strip() == "":
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, "Kevin AI\n\n", "welcome")
    output_text.config(state=tk.DISABLED)

input_frame = tk.Frame(root, bg=light_bg_colors[0])
input_frame.pack(pady=5, fill=tk.X)

input_text = scrolledtext.ScrolledText(input_frame, width=80, height=1)
input_text.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

send_button = tk.Button(input_frame, text="Send", command=send_question)
send_button.pack(side=tk.LEFT, padx=5)

input_text.bind("<Return>", send_question)

token_label = tk.Label(root, text=f"Tokens consumed: 0, Remaining tokens: {tokens_limit}", bg=light_bg_colors[0])
token_label.pack(pady=5)

model = original_models["qwen3"]
system_prompt = model_prompts.get(model)
conversation = [
    {
        "role": "system",
        "content": system_prompt
    }
]

settings_window = None

def open_settings():
    global settings_window, context_count
    if settings_window and settings_window.winfo_exists():
        settings_window.lift()
        return
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings - Powered by Kevin")
    bg_label = tk.Label(settings_window, text="Select Background Color:")
    bg_label.pack(pady=5)
    bg_var = tk.StringVar(settings_window)
    bg_var.set(light_bg_colors[0])
    bg_menu = tk.OptionMenu(settings_window, bg_var, *light_bg_colors, command=lambda color: change_bg(color))
    bg_menu.pack(pady=5)
    prompt_label = tk.Label(settings_window, text="Set Prompt")
    prompt_label.pack(pady=5)
    prompt_entry = tk.Entry(settings_window, width=85)
    prompt_entry.insert(0, system_prompt)
    prompt_entry.pack(pady=5)
    save_prompt_button = tk.Button(settings_window, text="Save Prompt",
                                   command=lambda: save_prompt(prompt_entry.get()))
    save_prompt_button.pack(pady=5)
    context_label = tk.Label(settings_window, text="Select Context Message Count:")
    context_label.pack(pady=5)
    context_var = tk.StringVar(settings_window)
    context_var.set(context_count)
    context_options = ["None", "1",  "5", "10", "20", "Unlimited"]
    context_menu = tk.OptionMenu(settings_window, context_var, *context_options,
                                 command=lambda value: set_context_count(value))
    context_menu.pack(pady=5)
    help_button = tk.Button(settings_window, text="View Model Help", command=show_model_help)
    help_button.pack(pady=5)
    thanks_label = tk.Label(settings_window, text="喜欢就给我一个star吧，我会持续更新的！")
    thanks_label.pack(pady=5)
    close_button = tk.Button(settings_window, text="Close Settings", command=settings_window.destroy)
    close_button.pack(pady=20)

def set_context_count(value):
    global context_count
    context_count = value

def change_bg(color):
    root.configure(bg=color)
    model_frame.configure(bg=color)
    output_text.configure(bg=color)
    input_frame.configure(bg=color)
    token_label.configure(bg=color)

def save_prompt(new_prompt):
    global system_prompt, conversation
    system_prompt = new_prompt
    conversation = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]
    messagebox.showinfo("Prompt Settings", "Prompt saved.")

def show_model_help():
    model_help_text = "Model number correspondence information is as follows:\n"
    model_help_text += "1: deepseek-reasoner\n"
    model_help_text += "2: yi\n"
    model_help_text += "3: Tongyi Qianwen (qwen2.5)\n"
    model_help_text += "4: chatglm\n"
    model_help_text += "5: black-forest-labs/FLUX.1-schnelln\n"
    model_help_text += "5: black-forest-labs/FLUX.1-schnelln\n"
    model_help_text +=  """kkkkk
    
"""
    
    messagebox.showinfo("Model Help", model_help_text)

settings_button = tk.Button(root, text="Settings", command=open_settings)
settings_button.pack(pady=10)

stop_button = tk.Canvas(input_frame, width=30, height=30, bg=light_bg_colors[0], highlightthickness=0)
stop_button.create_oval(5, 5, 25, 25, fill="white", outline="black")
stop_button.create_rectangle(10, 10, 20, 20, fill="blue", outline="blue")
stop_button.pack(side=tk.LEFT, padx=5)
stop_button.bind("<Button-1>", lambda event: stop_event.set())

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

root.after(5000, save_history)
root.mainloop()