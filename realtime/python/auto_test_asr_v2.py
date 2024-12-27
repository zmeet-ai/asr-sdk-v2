#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import websockets
from websockets.client import WebSocketClientProtocol
import os, sys, hmac, hashlib, time
from urllib.parse import quote
import orjson,json
import random, base64
from loguru import logger
import argparse
from dotenv import load_dotenv
load_dotenv()

time_per_chunk = 0.2  # 每次发送的音频数据的时间长度，单位：s
num_channel = 1  # 声道数
num_quantify = 16  # 量化位数
sample_rate = 16000  # 采样频率
bytes_per_chunk = int(sample_rate * num_quantify * time_per_chunk * num_channel / 8)
sleep_time_duration = 0.1 # 每次发送音频数据后等待的时间长度，单位：s

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), "../dataset/asr"))

async def send_audio_data(websocket: WebSocketClientProtocol, audio_file: str):
    try:
        filename = audio_file
        chunk_size = bytes_per_chunk
        
        with open(filename, "rb") as file:
            while True:
                sleep_time = time.time()
                data = file.read(chunk_size)
                if not data:
                    break
                await websocket.send(data)
                if (time.time() - sleep_time) < sleep_time_duration:
                    await asyncio.sleep(abs(sleep_time_duration - (time.time() - sleep_time)))
                sleep_time = time.time()
                await asyncio.sleep(0)
        await websocket.send('')
        #await websocket.send('{"end": true}')
        await asyncio.sleep(120)
    except (websockets.exceptions.ConnectionClosedError, KeyboardInterrupt) as e:
        logger.info(f"Connection closed or interrupted: {e}")
    except Exception as e:
        logger.error(f"Error in send_audio_data: {e}")

async def receive_recognition_result(websocket: WebSocketClientProtocol, print_mode: str):
    try:
        while True:
            result = await websocket.recv()  # 接收语音识别结果
            if not result:
                break
            #print("Recognition result:", result)
            asr_json = orjson.loads(result)
            is_final = asr_json.get("is_final", False)
            seg_id = asr_json.get("seg_id", 0)
            asr = asr_json.get("asr", "")
            type = asr_json.get("type", "")
            if print_mode == "typewriter":
                if type == "asr":
                    # 打字机效果输出：根据 is_final 决定是否换行
                    if is_final:
                        print(f"\r{seg_id}:{asr}", flush=True)
                    else:
                        print(f"\r{seg_id}:{asr}", end="", flush=True)
            else:
                if is_final:
                    logger.warning(f"{asr_json}")
                else:
                    logger.info(f"{asr_json}")
        await asyncio.sleep(120)  # 释放控制权，允许其他任务执行
    except Exception as err:
        print(f"receive_recognition_result error: {repr(err)}")

def generate_signature(app_id: str, api_key: str) -> str:
    """
    @param app_id: 应用程序ID
    @param api_key: 应用程序秘钥
    @return: 签名, 时间戳
    """
    ts: str = str(int(time.time()))
    tt = (app_id + ts).encode('utf-8')
    md5 = hashlib.md5()
    md5.update(tt)
    baseString = md5.hexdigest()
    baseString = bytes(baseString, encoding='utf-8')

    apiKey = api_key.encode('utf-8')
    signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
    signa = base64.b64encode(signa)
    signa = str(signa, 'utf-8')
    return signa, ts

async def connect_to_server(print_mode: str, asr_type: str, audio_file: str):
    # 请向公司商务申请账号
    app_id = os.getenv("ZMEET_APP_ID")
    app_secret = os.getenv("ZMEET_APP_SECRET")
    logger.info(f"app_id: {app_id}, app_secret: {app_secret}")
    base_url = "wss://{}/asr-realtime/v2/ws".format("audio.abcpen.com:8443")
    #base_url = "ws://{}/asr-realtime/v2/ws".format("192.168.2.141:2001")
    signa, ts = generate_signature(app_id, app_secret)

    url_asr_apply = base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa) + f"&asr_type={asr_type}" + "&trans_mode=0" + "&target_lang=ru" + "&pd=court"
    
    try:
        async with websockets.connect(url_asr_apply) as websocket:
            task_send = asyncio.create_task(send_audio_data(websocket, audio_file))
            task_receive = asyncio.create_task(receive_recognition_result(websocket, print_mode))

            done, pending = await asyncio.wait(
                [task_receive, task_send], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 取消所有未完成的任务
            for task in pending:
                task.cancel()
            # 等待取消的任务完成
            await asyncio.gather(*pending, return_exceptions=True)
    except Exception as e:
        logger.error(f"Connection error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ASR Client')
    parser.add_argument('--mode', 
                       choices=['typewriter', 'json'],
                       default='typewriter',
                       help='Output mode: typewriter (default) or json')
    parser.add_argument('--asr_type',
                       choices=['sentence', 'word'],
                       default='word',
                       help='ASR recognition mode: sentence (default) or word')
    parser.add_argument('--audio_file',
                       type=str,
                       default=os.path.join(os.path.dirname(__file__), "../dataset/asr/3-1-60s.wav"),
                       help='Path to the audio file (default: ../dataset/asr/3-1-60s.wav)')
    
    args = parser.parse_args()
    try:
        asyncio.run(connect_to_server(args.mode, args.asr_type, args.audio_file))
    except KeyboardInterrupt:
        logger.info("Program terminated by user (Ctrl+C)")
    except Exception as e: 
        logger.error(f"connect_to_server error: {repr(e)}")
