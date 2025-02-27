#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import base64
import requests
from loguru import logger
import argparse
from datetime import datetime, timedelta
import hashlib
import hmac

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from config import Config

class AudioStorageTest:
    def __init__(self, api_url: str = Config.API_URLS["dev"]):
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
        """获取请求头"""
        signature, ts = self.generate_signature()
        return {
            "X-App-Key": self.app_id,
            "X-App-Signature": signature,
            "X-Timestamp": ts,
        }

    def test_get_audio_record(self, task_id: str) -> None:
        """测试获取音频记录
        
        Args:
            task_id: 任务ID
        """
        url = f"{self.api_url}/asr/v2/audio/record/{task_id}"
        headers = self.get_headers()
        
        try:
            logger.info(f"Testing get audio record for task: {task_id}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result["code"] == "0":
                logger.info("Get audio record test passed")
            else:
                logger.error(f"Get audio record test failed: {result['message']}")
                
        except Exception as e:
            logger.error(f"Get audio record test failed with error: {str(e)}")
            raise

    def test_delete_audio_record(self, task_id: str) -> None:
        """测试删除音频记录
        
        Args:
            task_id: 任务ID
        """
        url = f"{self.api_url}/asr/v2/audio/record/{task_id}"
        headers = self.get_headers()
        
        try:
            logger.info(f"Testing delete audio record for task: {task_id}")
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result["code"] == "0":
                logger.info("Delete audio record test passed")
            else:
                logger.error(f"Delete audio record test failed: {result['message']}")
                
        except Exception as e:
            logger.error(f"Delete audio record test failed with error: {str(e)}")
            raise

    def test_get_app_records(self, 
                           start_time: datetime = None,
                           end_time: datetime = None,
                           limit: int = 10,
                           offset: int = 0) -> None:
        """测试获取应用的音频记录列表
        
        Args:
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            limit: 返回记录数量限制
            offset: 分页偏移量
        """
        url = f"{self.api_url}/asr/v2/audio/records"
        headers = self.get_headers()
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        
        try:
            logger.info("Testing get app records")
            logger.info(f"Parameters: {params}")
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result["code"] == "0":
                logger.info(f"Get app records test passed. Total records: {result['data']['total']}")
            else:
                logger.error(f"Get app records test failed: {result['message']}")
                
        except Exception as e:
            logger.error(f"Get app records test failed with error: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(
        description="Audio Storage API Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-t", "--task-id",
        type=str,
        help="Task ID for testing specific record operations"
    )
    args = parser.parse_args()

    client = AudioStorageTest()
    
    try:
        # 如果提供了task_id，测试特定记录的操作
        if args.task_id:
            client.test_get_audio_record(args.task_id)
            client.test_delete_audio_record(args.task_id)
        
        # 测试获取记录列表
        # 测试不带时间过滤
        client.test_get_app_records()
        
        # 测试带时间过滤
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        client.test_get_app_records(
            start_time=start_time,
            end_time=end_time,
            limit=5
        )

    except KeyboardInterrupt:
        logger.error("Test interrupted by user")
    except Exception as err:
        logger.error(f"Test failed: {repr(err)}")

if __name__ == "__main__":
    main()