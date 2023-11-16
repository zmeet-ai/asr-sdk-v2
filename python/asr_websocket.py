#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import websockets
from websockets.client import WebSocketClientProtocol
import os, sys, hmac, hashlib, time
from urllib.parse import quote
import json
import random, base64
import wave
import numpy as np
from loguru import logger

time_per_chunk = 0.1  # 多长时间发送一次音频数据，单位：s
num_channel = 1  # 声道数
num_quantify = 16  # 量化位数
sample_rate = 16000  # 采样频率
bytes_per_chunk = int(sample_rate * num_quantify * time_per_chunk * num_channel / 8)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../dataset"))

API_URL = "wss://asr-dev.abcpen.com"


def generate_signature(app_id: str, api_key: str) -> str:
    """
    @param app_id: 应用程序ID
    @param api_key: 应用程序秘钥
    @return: 签名, 时间戳
    """
    ts: str = str(int(time.time()))
    tt = (app_id + ts).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(tt)
    baseString = md5.hexdigest()
    baseString = bytes(baseString, encoding="utf-8")

    apiKey = api_key.encode("utf-8")
    signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
    signa = base64.b64encode(signa)
    signa = str(signa, "utf-8")
    return signa, ts


async def send_audio_data(websocket: WebSocketClientProtocol):
    filename = os.path.join(os.path.dirname(__file__), "../dataset/test.wav")  # 10分钟音频
    with wave.open(filename) as f:
        wave_file_sample_rate = f.getframerate()
        num_channels = f.getnchannels()
        assert f.getsampwidth() == 2, f.getsampwidth()
        num_samples = f.getnframes()
        samples = f.readframes(num_samples)
        logger.info(
            f"num_samples： {num_samples}， samples length: {len(samples)}"
        )  # num_samples： 9600000， samples length: 19200000

    # simulate streaming
    chunk_size = int(time_per_chunk * wave_file_sample_rate * 2)  # 0.1 seconds
    start = 0
    while start < num_samples * 2:
        end = start + chunk_size
        end = min(end, num_samples * 2)
        await websocket.send(samples[start:end])
        # logger.info(f"start: {start}, end: {end}")
        start = end

        await asyncio.sleep(0.03)
    logger.info(
        "\r-------------------------------------------------------------------------------------------"
    )


async def receive_recognition_result(websocket: WebSocketClientProtocol):
    try:
        seg_sentence = 0
        while True:
            result = await websocket.recv()  # 接收语音识别结果
            if not result:
                break
            asr_text = json.loads(result)
            asr = asr_text["asr"]
            asr_punc = ""
            if "asr_punc" in asr_text:
                asr_punc = asr_text["asr_punc"]
            seg_id = asr_text["seg_id"]
            is_final = asr_text["is_final"]
            if "translate" in asr_text:
                translate = asr_text["translate"]
            else:
                translate = ""
            if is_final:
                logger.info(
                    "\r{}:{} -> {}".format(seg_sentence, asr_punc, translate),
                    flush=True,
                )
                seg_sentence += 1
            else:
                logger.info(
                    "\r{}:{} -> {}".format(seg_sentence, asr, translate),
                    end="",
                    flush=True,
                )
                # pass
            await asyncio.sleep(0)
    except Exception as err:
        logger.info(f"\rreceive_recognition_result error: {err}")


async def connect_to_server():
    app_id = "test1"
    app_secret = "2258ACC4-199B-4DCB-B6F3-C2485C63E85A"

    base_url = f"{API_URL}/v2/asr/ws"
    signa, ts = generate_signature(app_id, app_secret)

    url_asr_apply = (
        base_url
        + "?appid="
        + app_id
        + "&ts="
        + ts
        + "&signa="
        + quote(signa)
        + "&asr_type=2"
        + "&trans_mode=1"
        + "&target_lang=ru"
        + "&pd=court"
    )

    async with websockets.connect(url_asr_apply) as websocket:
        task_send = asyncio.create_task(send_audio_data(websocket))
        task_receive = asyncio.create_task(receive_recognition_result(websocket))
        await asyncio.wait([task_receive, task_send], return_when=asyncio.ALL_COMPLETED)


if __name__ == "__main__":
    try:
        asyncio.run(connect_to_server())
    except KeyboardInterrupt as err:
        logger.error(f"keyboard exception: {err}")
    except Exception as e:
        logger.error(f"connect_to_server error: {e}")
        
"""
运行结果：

2023-11-10 14:09:28.887 | INFO     | __main__:send_audio_data:55 - num_samples： 64960， samples length: 129920
2023-11-10 14:09:28.888 | INFO     | __main__:send_audio_data:61 - samples_int16 length: 64960
2023-11-10 14:09:28.888 | INFO     | __main__:send_audio_data:64 - samples_float32 length: 64960
0:北 -> 10 14:09:29.497 | INFO     | __main__:receive_recognition_result:109 -
0:北京 ->  14:09:29.591 | INFO     | __main__:receive_recognition_result:109 -
0:北京科技 -> 09:29.682 | INFO     | __main__:receive_recognition_result:109 -
0:北京科技馆 -> :29.775 | INFO     | __main__:receive_recognition_result:109 -
-------------------------------------------------------------------------------------------
0:北京科技馆。 -> Пекинский научно-технический центр._recognition_result:103 -
"""