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

def update_logger():
    # 打印日志，方便追踪问题
    log_file = os.getenv("LOG_FILE", "/data/logs/asr/asr_test.log")
    log_dir = os.path.dirname(log_file)
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    log_level = os.getenv("LOG_LEVEL", "DEBUG")
    max_file_size = 100 * 1024 * 1024  # 100 MB

    # 配置默认的控制台处理器
    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan> | {file}:{function}:{line}",
                "colorize": True,
                "level": log_level,
            }
        ]
    )

    # 添加文件日志处理器
    logger.add(
        log_file,
        rotation=max_file_size,  # Rotate when file size reaches 100MB
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message} | {file}:{function}:{line}",
        level=log_level,
    )
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
            if args.print_voiceprint == "1":
                asr_corrected = asr_json.get("asr_corrected", "")
                if len(asr_corrected) > 0:
                    speaker = asr_json.get("speaker", "")
                    print(f"\r{speaker}: {asr_corrected}", flush=True)
            else:
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

async def connect_to_server(print_mode: str, asr_type: str, audio_file: str, metadata: str):
    app_id = os.getenv("ZMEET_APP_ID")
    app_secret = os.getenv("ZMEET_APP_SECRET")
    logger.info(f"metadata: {metadata}, type: {type(metadata)}")
    if not app_id or not app_secret:
        raise ValueError("缺少必需的环境变量：ZMEET_APP_ID 或 ZMEET_APP_SECRET 未设置")
    
    base_url = "wss://audio.abcpen.com:8443/asr-realtime/v2/ws"
    #base_url = "ws://127.0.0.1:2001/asr-realtime/v2/ws"
    signa, ts = generate_signature(app_id, app_secret)
    
    # 更新 URL，添加声纹识别参数
    url = (f"{base_url}?appid={app_id}&ts={ts}&signa={quote(signa)}"
           f"&asr_type={asr_type}&voiceprint={args.voiceprint}"
           f"&voiceprint_org_id={args.voiceprint_org_id}"
           f"&word_time={args.word_time}"
           f"&voiceprint_tag_id={args.voiceprint_tag_id}"
           f"&translate_mode={args.translate_mode}"
           f"&target_language={args.target_language}"
           f"&audio_channels=1"
           f"&active_channel=merge"
           f"&metadata={quote(args.metadata)}")
    
    try:
        async with websockets.connect(url) as websocket:
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
                       default=os.path.join(os.path.dirname(__file__), "../dataset/asr/1006_20241223_081645_full_audio.wav"),
                       help='Path to the audio file (default: ../dataset/asr/1006_20241223_081645_full_audio.wav)')
    parser.add_argument('--voiceprint',
                       type=str,
                       default='1',
                       help='Enable voiceprint recognition (default: 1)')
    parser.add_argument('--voiceprint_org_id',
                       type=str,
                       default=None,  # 将使用 app_id 作为默认值
                       help='Organization ID for voiceprint (default: same as app_id)')
    parser.add_argument('--voiceprint_tag_id',
                       type=str,
                       default=None,  # 将使用 app_id 作为默认值
                       help='Tag ID for voiceprint (default: same as app_id)')
    parser.add_argument('--print_voiceprint',
                       type=str,
                       default='0',
                       choices=['0', '1'],
                       help='Enable voiceprint result printing (0: disabled, 1: enabled)')
    parser.add_argument('--word_time',
                       type=str,
                       default='0',
                       choices=['0', '1'],
                       help='Enable word-level timing output (0: disabled, 1: enabled)')
    parser.add_argument('--translate_mode',
                       type=str,
                       default='0',
                       choices=['0', '1'],
                       help='Enable translation (0: disabled, 1: enabled)')
    parser.add_argument('--target_language',
                       type=str,
                       default='en',
                       help='Target language for translation')
    # 用户自定义的metadata, 直接回传给客户, 这里仅作示例，可以传递任意json字符串（stringfy）
    metadata_sample = {
        "user_name": "John",
    }
    parser.add_argument('--metadata',
                       type=str,
                       default=json.dumps(metadata_sample, ensure_ascii=False),
                       help='Metadata for the request, callback to client (JSON string)')

    args = parser.parse_args()
    
    # 如果未指定 org_id 和 tag_id，使用 app_id
    app_id = os.getenv("ZMEET_APP_ID")
    if args.voiceprint_org_id is None:
        args.voiceprint_org_id = app_id
    if args.voiceprint_tag_id is None:
        args.voiceprint_tag_id = app_id
    update_logger()
    logger.info(f"\n{'*'*50} \n asr realtime start \n{'*'*50}\n")
    asyncio.run(connect_to_server(args.mode, args.asr_type, args.audio_file, args.metadata))
