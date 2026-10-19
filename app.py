import os

from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent


# ตรวจสอบว่ากำหนดค่าจำเป็นครบก่อนเริ่มแอป
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not CHANNEL_SECRET:
    raise RuntimeError("กรุณากำหนด environment variable: LINE_CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN:
    raise RuntimeError(
        "กรุณากำหนด environment variable: LINE_CHANNEL_ACCESS_TOKEN"
    )

app = Flask(__name__)

handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)


@app.route("/", methods=["GET"])
def home():
    return "LINE Webhook is running", 200


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.warning("LINE Webhook received an invalid signature.")
        abort(400, description="Invalid signature")

    return "OK", 200


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    # ใช้ reply token ตอบกลับข้อความที่ได้รับจาก LINE
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        line_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text="สวัสดีครับ LINE Bot ทำงานแล้ว")
                ],
            )
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    # debug=False เพื่อไม่เปิด debugger ในการรันปกติ
    app.run(host="0.0.0.0", port=port, debug=False)
