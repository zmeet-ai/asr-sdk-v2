#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os
import sys
import hmac
import hashlib
import time
import base64
import json
from dataclasses import dataclass
from typing import Optional, Union
from urllib.parse import quote
from time import perf_counter
from loguru import logger
import argparse

from config import Config
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

@dataclass
class AsrRequest:
    language: str = "zh"
    fast: bool = True
    audio_file: Optional[bytes] = None
    audio_url: Optional[str] = None
    vocab_id: Optional[str] = None
    voiceprint_enabled: bool = True
    voiceprint_org_id: Optional[str] = None
    voiceprint_tag_id: Optional[str] = None

class AsrClient:
    def __init__(self, api_url: str = Config.API_URLS["prd"]):
        self.api_url = api_url
        self.app_id = Config.APP_ID
        self.app_secret = Config.APP_SECRET

    def generate_signature(self) -> tuple[str, str]:
        """生成API调用签名
        
        Returns:
            tuple: (signature, timestamp)
        """
        ts = str(int(time.time()))
        tt = (self.app_id + ts).encode("utf-8")
        md5 = hashlib.md5()
        md5.update(tt)
        base_string = md5.hexdigest().encode("utf-8")
        
        api_key = self.app_secret.encode("utf-8")
        signature = hmac.new(api_key, base_string, hashlib.sha1).digest()
        signature = base64.b64encode(signature).decode("utf-8")
        
        return signature, ts

    def get_headers(self) -> dict:
        """获取请求头
        
        Returns:
            dict: 包含认证信息的请求头
        """
        signature, ts = self.generate_signature()
        return {
            "X-App-Key": self.app_id,
            "X-App-Signature": signature,
            "X-Timestamp": ts,
        }

    def test_sentence(self, request: AsrRequest, use_json: bool = False) -> dict:
        """测试语音识别接口
        
        Args:
            request: 请求参数
            use_json: 是否使用JSON格式发送请求
            
        Returns:
            dict: 识别结果和声纹识别结果
        """
        url = f"{self.api_url}/sentence/v2/sentence"
        headers = self.get_headers()
        
        try:
            t = perf_counter()
            
            if use_json:
                data = request.__dict__
                if request.audio_file:
                    data["audio_file"] = base64.b64encode(request.audio_file).decode()
                    data["voiceprint_enabled"] = True
                    data["voiceprint_org_id"] = self.app_id
                    data["voiceprint_tag_id"] = self.app_id
                    logger.info(f"audio file for json data: {data}")
                response = requests.post(url, headers=headers, json=data)
            else:
                if request.audio_file:
                    files = {"audio_file": request.audio_file}
                    data = {
                        "language": request.language,
                        "fast": request.fast,
                        "voiceprint_enabled": True,
                        "voiceprint_org_id": self.app_id,
                        "voiceprint_tag_id": self.app_id
                    }
                    logger.info(f"audio file for form data: {data}")
                    response = requests.post(url, headers=headers, files=files, data=data)
                else:
                    data = request.__dict__
                    data["voiceprint_enabled"] = True
                    data["voiceprint_org_id"] = self.app_id
                    data["voiceprint_tag_id"] = self.app_id
                    logger.info(f"{'-'*100}audio file for form data: {data}")
                    response = requests.post(url, headers=headers, data=data)

            response.raise_for_status()
            result = response.json()
            
            logger.info(f"ASR Result: {result['data']['asr']}")
            logger.info(f"Speaker: {result['data']['speaker']}")
            logger.info(f"Processing time: {perf_counter() - t:.5f}s")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(
        description="ASR Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-l", "--language",
        type=str,
        default="zh",
        choices=["zh", "en", "ru"],
        help="Select audio language to test"
    )
    args = parser.parse_args()

    client = AsrClient()
    
    try:
        for i in range(1):
            # 使用文件测试
            with open(Config.AUDIO_FILES[args.language]["file"], "rb") as f:
                request = AsrRequest(
                    language=args.language,
                    audio_file=f.read()
                )
                client.test_sentence(request, use_json=False)

            # 使用URL测试
            request = AsrRequest(
                language=args.language,
                audio_url=Config.AUDIO_FILES[args.language]["url"]
            )
            client.test_sentence(request, use_json=False)

    except KeyboardInterrupt:
        logger.error("Test interrupted by user")
    except Exception as err:
        logger.error(f"Test failed: {repr(err)}")

if __name__ == "__main__":
    main()
