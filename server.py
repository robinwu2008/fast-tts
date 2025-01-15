import binascii
from quart import Quart, request, jsonify, Response, render_template
import json
import edge_tts

app = Quart(__name__)

@app.route('/gen-tts',methods=['GET'])
async def gentts():
    content = request.args.get("content")
    voice = request.args.get("voice")
    print("content=%s, voice=%s" % (content,voice))

    headers = {
        'Transfer-Encoding': 'chunked',
        'Content-Type': 'audio/mpeg',
        # 设置 Cache-Control 头
        'Cache-Control': 'public, max-age=3600'  # 音频流缓存1小时
    }
    response_content = ms_tts_async(content, voice)
    return Response(response_content, headers=headers)

@app.route('/gen',methods=['GET'])
async def gen():
    content = request.args.get("content")
    voice = request.args.get("voice")
    bra_id=request.args.get("braId")
    token=request.args.get("token")
    print("content=%s, voice=%s,bra_id=%s" % (content,voice,bra_id))

    headers = {
        'Transfer-Encoding': 'chunked',
        'Content-Type': 'audio/mpeg',
        # 设置 Cache-Control 头
        'Cache-Control': 'public, max-age=3600'  # 音频流缓存1小时
    }
    response_content = ms_tts_async(content, voice)
    return Response(response_content, headers=headers)

async def ms_tts_async(text_input, voice="zh-CN-XiaoxiaoNeural"):
    communicate = edge_tts.Communicate(text_input, voice)
    async for chunked in communicate.stream():
        if chunked["type"] == "audio":
            yield chunked["data"]


if __name__ == '__main__':
    app.run()