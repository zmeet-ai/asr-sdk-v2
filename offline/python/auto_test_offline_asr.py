#! /usr/bin/env python3

import requests
import time
import uuid
import hashlib
import hmac
import base64
import os
import dotenv
import json
dotenv.load_dotenv()

# FastAPI 服务的 URL
BASE_URL = "https://audio.abcpen.com:8443"


application_key = os.getenv("ZMEET_APP_ID")
application_secret = os.getenv("ZMEET_APP_SECRET")

# generate new signature for the request (client side)
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


expected_signature, timestamp = generate_signature(application_key, application_secret)
headers = {
    "X-App-Key": application_key,
    "X-App-Signature": expected_signature,
    "X-Timestamp": timestamp,
}

# 提交任务
def submit_task(audio_url, app_id, task_id, language):
    response = requests.post(
        f"{BASE_URL}/asr-offline/submit_task/v1",
        json={
            "audio_url": audio_url,
            "app_id": app_id,
            "org_id": app_id,
            "tag_id": app_id,
            "task_id": task_id,
            "language": language,
            "audio_type": "asr_sd",
            "max_speaker_num": 2,
            "min_speaker_num": 2,
            "word_timestamp": True
        },
        headers=headers
    )
    return response.json()

# 检查任务状态
def check_status(task_id):
    response = requests.get(f"{BASE_URL}/asr-offline/check_status/v1/{task_id}", headers=headers)
    return response.json()

# 获取任务结果
def get_result(task_id):
    response = requests.get(f"{BASE_URL}/asr-offline/get_result/v1/{task_id}", headers=headers)
    return response.json()

# 主函数
def main():
    audio_url = "https://zos.abcpen.com/test/1006_20241223_081645_full_audio.wav"
    app_id = os.getenv("ZMEET_APP_ID")
    task_id = str(uuid.uuid4())
    language = "zh"

    # 提交任务
    submit_response = submit_task(audio_url, app_id, task_id, language)
    print("Submit Response:", submit_response)

    # 循环检测任务状态
    while True:
        status_response = check_status(task_id)
        print("Status Response:", status_response)

        if status_response["status"] == "completed":
            print("Task completed!")
            break
        elif status_response["status"] == "not_found":
            print("Task not found or expired!")
            break
        else:
            print("Task is still processing...")

        # 等待一段时间后再次检查
        time.sleep(5)

    # 获取任务结果
    result_response = get_result(task_id)
    print("Result Response:", result_response)
    
    # 保存结果到JSON文件
    output_filename = f"asr_result_{task_id}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(result_response, f, ensure_ascii=False, indent=4)
    print(f"结果已保存到文件: {output_filename}")

if __name__ == "__main__":
    main()