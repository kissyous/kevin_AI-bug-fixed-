# Model Interaction Interface

## 项目概述
这是一个基于Python和Tkinter构建的AI模型交互界面，支持多种AI模型调用和交互功能。

## 主要功能
- **多模型支持**：支持普通模型和备用模型切换
- **令牌管理**：实时跟踪令牌使用情况
- **上下文管理**：可配置上下文消息数量
- **个性化设置**：支持背景颜色、提示词等自定义

## 技术栈
- Python 3.9+
- Tkinter GUI
- OpenAI API

## 安装使用
1. 安装依赖：
```bash
pip install openai

##配置API密钥：

original_api_key = "your_api_key"
backup_api_key = "your_backup_key"

运行程序：
python en.py

#代码结构

# 主要模块
def create_completion():  # 处理模型请求
def send_question():      # 发送用户问题
def select_model():       # 模型选择功能
使用说明
从下拉菜单选择模型
在输入框输入问题
点击Send或按回车发送
在设置中可调整背景色等参数
注意事项
请妥善保管API密钥
注意令牌使用限制
备用模型会在主模型达到限制时自动启用
#贡献指南
欢迎提交issue或PR

#许可证
请不要用于商业用途！！！
