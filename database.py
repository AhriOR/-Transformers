import pyodbc
import re
#配置pyodbc
conn = pyodbc.connect(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=localhost;'
    r'DATABASE=Translation;'
    r'Trusted_Connection=yes;'
)
cursor = conn.cursor()

def check_user(username, password):
    """检查用户函数"""
    cursor.execute("EXEC GetUserByUsername ?", username)
    row = cursor.fetchone()
    if row and row[1] == password:
        return True
    return False

def register_user(username, password):
    """用户注册函数"""
    cursor.execute("EXEC GetUserByUsername ?", username)
    if cursor.fetchone():
        return False
    try:
        cursor.execute("INSERT INTO Users (Username, Password) VALUES (?, ?)", username, password)
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

def save_translation(username, original_text, translated_text, direction):
    """保存翻译历史"""
    cursor.execute("""
        INSERT INTO TranslationHistory (Username, OriginalText, TranslatedText, Direction)
        VALUES (?, ?, ?, ?)
    """, username, original_text, translated_text, direction)
    conn.commit()

def get_translation_history(username):
    """获取用户历史"""
    cursor.execute("EXEC GetTranslationHistoryByUser ?", username)
    return cursor.fetchall()
#判断是否为中文函数
def is_chinese(text):
    pattern = r'^[\u4e00-\u9fff。，！？、“”‘’（）《》【】…——\-·\s]+$'
    return bool(re.fullmatch(pattern, text))
#插入聊天记录函数
def insert_chat(username, user_msg, bot_reply):
    cursor.execute("INSERT INTO chat_history (username, user_msg, bot_reply) VALUES (?, ?, ?)",
                   (username, user_msg, bot_reply))
    conn.commit()

# 获取聊天记录的函数
def get_all_chat_history(username):
    cursor.execute("SELECT user_msg, bot_reply FROM chat_history WHERE username = ?", (username,))
    return cursor.fetchall()
