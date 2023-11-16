#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os, sys, hmac, hashlib, time, base64
from urllib.parse import quote
from time import perf_counter
from loguru import logger

API_URL = "https://asr-dev.abcpen.com"


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


def test_sentence(api_url, use_file):
    app_id = "test1"
    app_secret = "2258ACC4-199B-4DCB-B6F3-C2485C63E85A"
    signature, ts = generate_signature(app_id, app_secret)
    headers = {
        "X-App-Key": app_id,
        "X-App-Signature": signature,
        "X-Timestamp": ts,
    }
    if use_file:
        files = {"audio_file": open(f"dataset/3-1-60s.wav", "rb")}
        json = {"punc": True}
        url = f"{api_url}/v2/asr/sentence"

        r = requests.post(url, headers=headers, files=files, data=json)
    else:
        # files = {"audio_file": open(f"dataset/3-1-60s.wav", "rb")}
        json = {
            "punc": True,
            "audio_url": "https://zos.abcpen.com/tts/zmeet/20221023/b6a2c7ac-52c8-11ed-961e-00155dc6cbed.mp3",
        }
        url = f"{api_url}/v2/asr/sentence"

        r = requests.post(url, headers=headers, data=json)

    print(f"response: {r.text}")


if __name__ == "__main__":
    try:
        for i in range(2):
            t1 = perf_counter()
            test_sentence(API_URL, True)
            test_sentence(API_URL, False)
            print(f"time consume: {perf_counter() - t1:.5f}s")
            # time.sleep(0.1)
    except KeyboardInterrupt as err:
        logger.error(f"keyboard exception: {err}")
    except Exception as err:
        logger.error(f"exception: {err}")
