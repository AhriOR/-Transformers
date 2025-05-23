# -Transformers
# 🌐 MarianMT + Qwen 0.6B Gradio 应用

一个基于 Hugging Face `MarianMT` 和阿里 `Qwen-0.5B` 模型的多功能 Web 应用，使用 Gradio 构建，支持：

- 🔁 中英文双向翻译（MarianMT）
- 💬 多轮中文聊天对话（Qwen-0.6B）
- 👤 用户界面友好，开箱即用

---

## 🚀 功能特性

| 模块        | 描述                                    |
|-------------|-----------------------------------------|
| 翻译模块     | 支持中文 → 英文 和 英文 → 中文双向翻译      |
| 聊天模块     | 使用 Qwen 0.5B 模型进行中文多轮对话         |
| Gradio 界面 | 使用 Gradio 构建交互式 Web 前端             |

---

## 🧱 项目结构

```bash
.
├── app.py               # 主应用入口
├── database.py          # 与 sqlserver 交互模块
├── web.py               # ngrok 通道搭建网站
├── model_preserved.py   # 模型加载保存（不包含微调）          
├── requirements.txt     # 所需依赖
└── README.md            # 本文件

```


 
## 安装依赖： 
```bash

pip install -r requirements.txt


```

## ✍️ 作者想说的话
其实距离学习深度学习仅仅只有两个月的时间，我觉得自己啃代码啃着啃着能到这一步已经不错了，想想之前都是吃饭睡觉打游戏的生活。
接下来我也会持续更新完善，想让我集成什么功能可以提出来，我会尽力去办的。
