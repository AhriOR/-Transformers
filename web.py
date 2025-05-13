import threading
import webview
from pyngrok import ngrok, conf
import app
#ngrok-token
conf.get_default().auth_token = "2w8CMPQNo1KOsWCq5CtKxEV9wJo_2BM9zJXsLZ2ZL9GQ2zr1X"
# 设置 Gradio 运行端口
PORT = 7862
# 启动 Gradio 应用（运行在子线程中）
def start_gradio():
    app.demo.launch(server_name="0.0.0.0", server_port=PORT, show_error=True)
# 子线程启动 Gradio
thread = threading.Thread(target=start_gradio, daemon=True)
thread.start()
# 创建 ngrok 公网隧道
fixed_domain = "full-nice-possum.ngrok-free.app"
public_url = ngrok.connect(addr=PORT, proto="http", domain=fixed_domain).public_url

print(f"✅ 公网访问地址：{public_url}")
# 创建 PyWebView GUI 窗口，自动加载 ngrok 公网地址
webview.create_window("智能翻译", public_url, width=1200, height=800)
# 启动 WebView（自动加载网页）
webview.start()

