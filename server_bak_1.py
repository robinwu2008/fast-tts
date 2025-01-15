import binascii
from quart import Quart, request, jsonify, Response, render_template,send_file
import json
import edge_tts
import aiofiles
import os
from hashlib import md5
from gtts import gTTS

app = Quart(__name__)


@app.route('/')
async def home():
    return await render_template('home.html')


@app.route('/generate', methods=['POST'])
async def generate():
    data = await request.get_data()
    payload = binascii.hexlify(data).decode('utf8')
    t = {"code": 1, "audio_url": "/tts?payload=" + payload}
    return jsonify(t)


@app.route('/tts', methods=['GET'])
async def tts():
    payload = request.args.get("payload")
    plaintext = binascii.unhexlify(payload).decode('utf8')
    json_obj = json.loads(plaintext)
    content = json_obj["content"]
    voice = json_obj.get("voice", "zh-CN-XiaoxiaoNeural")
    headers = {'Transfer-Encoding': 'chunked', 'Content-Type': 'audio/mpeg'}
    response_content = ms_tts_async(content, voice)
    return Response(response_content, headers=headers)

@app.route('/gen',methods=['POST'])
async def gen():
    content = request.args.get("content")
    voice = request.args.get("voice")
    bra_id=request.args.get("bra_id")
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



@app.route('/gen-tts',methods=['GET'])
async def gentts():
    content = request.args.get("content")
    voice = request.args.get("voice")
    voice = request.args.get("api_key")

    headers = {'Transfer-Encoding': 'chunked', 'Content-Type': 'audio/mpeg'}

    headers = {
        'Transfer-Encoding': 'chunked',
        'Content-Type': 'audio/mpeg',
        # 设置 Cache-Control 头
        'Cache-Control': 'public, max-age=3600'  # 音频流缓存1小时
    }
    response_content = ms_tts_async(content, voice)
    return Response(response_content, headers=headers)

@app.route('/post-tts',methods=['POST'])
async def posttts():
    content = request.args.get("content")
    voice = request.args.get("voice")
    bra_id = request.args.get("bra_id")
    print("content=%s, bra_id=%s ,voice=%s" % (content,bra_id,voice))
    obj = md5()
    obj.update(content.encode("utf-8"))

    # 获取十六进制格式的哈希值
    content_hex = obj.hexdigest()

    #output_file='/data0/python/fnb/wav/bra_id/voice/'+content_hex+'.wav'
    #output_file="D:\data0\python\\fnb\wav\\bra_id"+content_hex+".wav"
    #base_path='D://data0/python/fnb/wav/'+bra_id
    #base_path = f"D:\\data0\\python\\fnb\\wav\\{bra_id}"
    base_path = f"D:\\data0\\python\\fnb\\wav\\{bra_id}"
    output_file = os.path.join(base_path, f"{content}.wav")
    if os.path.exists(output_file):
        print(f"{output_file} already exists. Returning file stream.")
        async with aiofiles.open(output_file, 'rb') as f:
            return await f.read()  # 返回文件流

    headers = {'Transfer-Encoding': 'chunked', 'Content-Type': 'audio/mpeg'}
    response_content =  ms_tts_async(content, voice)
    os.makedirs(base_path, exist_ok=True)
    await save_audio_to_file(response_content, output_file)
    response = Response(response_content, headers=headers)
    return response


async def ms_tts_async(text_input, voice):
    communicate = edge_tts.Communicate(text_input, voice)
    async for chunked in communicate.stream():
        if chunked["type"] == "audio":
            yield chunked["data"]


async def save_audio_to_file(audio_data, output_file):
    async with aiofiles.open(output_file, 'wb') as f:
        await f.write(audio_data)  # 写入文件





if __name__ == '__main__':
    app.run()
