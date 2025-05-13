import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, MarianTokenizer, MarianMTModel
import pyodbc
from database import check_user, register_user, save_translation, get_translation_history, is_chinese,insert_chat,get_all_chat_history
# 数据库连接
conn = pyodbc.connect(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=localhost;'
    r'DATABASE=Translation;'
    r'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# 模型加载
tokenizer_en2zh = MarianTokenizer.from_pretrained("./marianmt_en2zh")
model_en2zh = MarianMTModel.from_pretrained("./marianmt_en2zh")

tokenizer_zh2en = MarianTokenizer.from_pretrained("./marianmt_zh2en")
model_zh2en = MarianMTModel.from_pretrained("./marianmt_zh2en")

tokenizer = AutoTokenizer.from_pretrained('./Qwen3-0.6B')
model = AutoModelForCausalLM.from_pretrained('./Qwen3-0.6B')
pipe = pipeline('text-generation', model=model, tokenizer=tokenizer)

# 当前设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_en2zh = model_en2zh.to(device)
model_zh2en = model_zh2en.to(device)

# 登录
def login(username, password):
    if check_user(username, password):
        return "✅ 登录成功", True, username
    return "❌ 登录失败，用户名或密码错误", False, ""

# 注册
def register(username, password):
    if register_user(username, password):
        return "✅ 注册成功"
    else:
        return "❌ 注册失败，用户名已存在或系统错误"

# 翻译
def translate(text, direction, is_logged_in, username):
    if not is_logged_in:
        return "⚠️ 请先登录", []

    if direction == "英译中":
        if not is_chinese(text):
            tokenizer_use, model_use = tokenizer_en2zh, model_en2zh
        else:
            msg = "⚠️ 输入不是英文"
            save_translation(username, text, msg, direction)
            return msg, get_translation_history(username)
    elif direction == "中译英":
        if is_chinese(text):
            tokenizer_use, model_use = tokenizer_zh2en, model_zh2en
        else:
            msg = "⚠️ 输入不是中文"
            save_translation(username, text, msg, direction)
            return msg, get_translation_history(username)
    else:
        return "❌ 不支持的翻译方向", []

    try:
        inputs = tokenizer_use(text, return_tensors="pt", padding=True, truncation=True).to(device)
        decode = model_use.generate(**inputs, max_length=128, num_beams=4)
        output = tokenizer_use.decode(decode[0], skip_special_tokens=True)
    except Exception as e:
        output = f"⚠️ 翻译出错: {str(e)}"

    save_translation(username, text, output, direction)
    history = get_translation_history(username)
    return output, history

# 登出
def logout(confirm, current_login_state, current_username_state):
    if confirm == "是":
        return "👋 已退出登录", False, ""
    else:
        return "✅ 继续使用", current_login_state, current_username_state


# 聊天逻辑函数（一次返回一条消息）
def chatbot_function(user_msg, username, is_login):
    if not is_login:
        return "⚠️ 请先登录才能聊天。"

    prompt = f"""
    你是一个专业中文智能助手，能够清晰、准确、简洁地回答用户的问题。
    请根据用户输入，给予专业而友好的回答。
    
    用户输入：{user_msg}
    助手回答：
    """
    output = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.6, return_full_text=False)
    bot_output = output[0]['generated_text'].replace(prompt,"").strip()

    insert_chat(username, user_msg, bot_output)
    return bot_output

# 查看历史聊天记录的函数
def show_chat_history(username):
    chat_history = get_all_chat_history(username)
    chat_history_text = "\n".join([f"你: {msg[0]}\n机器人: {msg[1]}" for msg in chat_history])
    return chat_history_text if chat_history else "没有找到聊天记录。"
# Gradio 应用 UI
with gr.Blocks(title="🌐 AI机器翻译小程序") as demo:
    login_state = gr.State(value=False)
    username_state = gr.State("")

    gr.Markdown("# 🌍 智能翻译助手\n轻松实现中英互译，体验智能 AI 的魅力！")

    with gr.Tab("🔐 登录"):
        gr.Markdown("### 🙋‍♂️ 欢迎回来！请登录以继续使用翻译功能")

        with gr.Row():
            with gr.Column():
                username_input = gr.Textbox(label="👤 用户名", placeholder="输入你的用户名")
                password_input = gr.Textbox(label="🔒 密码", type="password", placeholder="输入你的密码")
                login_button = gr.Button("🔓 登录", variant="primary")

            with gr.Column():
                login_status = gr.Textbox(label="登录状态", interactive=False)

        login_button.click(
            login,
            inputs=[username_input, password_input],
            outputs=[login_status, login_state, username_state]
        )

    with gr.Tab("注册"):
        gr.Markdown("### 📜 注册新账号")

        with gr.Row():
            with gr.Column():
                new_username_input = gr.Textbox(label="👤 用户名", placeholder="输入你的新用户名")
                new_password_input = gr.Textbox(label="🔒 密码", type="password", placeholder="设置你的密码")
                register_button = gr.Button("🔑 注册", variant="primary")

            with gr.Column():
                register_status = gr.Textbox(label="注册状态", interactive=False)

        register_button.click(
            register,
            inputs=[new_username_input, new_password_input],
            outputs=[register_status]
        )

    with gr.Tab("🤖 聊天机器人"):
        gr.Markdown("### 💬 开始聊天")

        user_input = gr.Textbox(label="输入你的消息...", placeholder="说点什么吧")
        submit_btn = gr.Button("发送")
        bot_reply_box = gr.Textbox(label="机器人回复", interactive=False, lines=3)

        # 查看聊天记录按钮
        view_history_btn = gr.Button("查看聊天记录")
        chat_history_output = gr.Textbox(label="聊天记录", interactive=False, lines=10)

        submit_btn.click(
            fn=chatbot_function,
            inputs=[user_input, username_state, login_state],
            outputs=[bot_reply_box]
        )

        # 点击查看聊天记录按钮时显示历史记录
        view_history_btn.click(
            fn=show_chat_history,
            inputs=[username_state],
            outputs=[chat_history_output]
        )

    with gr.Tab("🌐 翻译"):
        gr.Markdown("### 🌐 输入要翻译的内容并选择方向")

        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(label="输入文本", lines=4, placeholder="请输入要翻译的文本")
                direction = gr.Dropdown(["英译中", "中译英"], label="翻译方向", value="英译中")
                translate_btn = gr.Button("🚀 开始翻译", variant="primary")
                translated = gr.Textbox(label="翻译结果", lines=4, interactive=False)

            with gr.Column():
                history = gr.Dataframe(headers=["原文", "译文", "方向"], label="📜 翻译历史", interactive=False, row_count=(10, "fixed"))

        translate_btn.click(
            translate,
            inputs=[input_text, direction, login_state, username_state],
            outputs=[translated, history]
        )

    with gr.Tab("🚪 退出登录"):
        gr.Markdown("### 🚪 是否确认退出登录？")

        with gr.Row():
            with gr.Column():
                logout_radio = gr.Radio(["是", "否"], label="请选择")
                logout_btn = gr.Button("✅ 提交", variant="secondary")

            with gr.Column():
                logout_status = gr.Textbox(label="退出状态", interactive=False)

        logout_btn.click(
            logout,
            inputs=[logout_radio, login_state, username_state],
            outputs=[logout_status, login_state, username_state]
        )

if __name__ == "__main__":
    demo.launch(share=True)
