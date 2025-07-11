import os
from flask import Flask, request, jsonify
import dashscope
import requests

app = Flask(__name__)
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

@app.route("/api/qwen-tts", methods=["POST"])
def qwen_tts():
    data = request.get_json()
    text = data.get("text", "")
    voice = data.get("voice", "Cherry")
    model = data.get("model", "qwen-tts-latest")

    if not text:
        return jsonify({"error": "参数 `text` 不能为空"}), 400

    try:
        response = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
            model=model,
            text=text,
            voice=voice
        )
    except Exception as e:
        return jsonify({"error": f"TTS 调用失败: {e}"}), 500

    if not response or not hasattr(response.output, "audio"):
        return jsonify({"error": "接口未返回 audio.url"}), 500

    audio_url = response.output.audio["url"]
    return jsonify({"audioUrl": audio_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

