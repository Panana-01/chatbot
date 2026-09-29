# Venem

命令行和本地网页聊天机器人。回复来自现有的意图匹配、闲聊、问答、身份管理和厨房库存逻辑。

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## 运行

命令行：

```powershell
.\.venv\Scripts\python chatbot_demo.py
```

输入 `exit` 或 `quit` 结束。

本地网页：

```powershell
.\.venv\Scripts\python -m streamlit run app.py
```

浏览器打开后，同一会话会保留对话、名字和厨房库存。侧栏的 New conversation 会开始一次新会话。
