#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config:
    API_URLS = {
        "local": "http://127.0.0.1:2001",
        "dev": "http://192.168.2.141:2001",
        "pre": "https://asr-pre.abcpen.com:8443",
        "prd": "https://audio.abcpen.com:8443",
    }
    
    AUDIO_FILES = {
        "zh": {
            "file": "../dataset/voiceid/verify/1006_20241223_194521_user_audio_0000.wav",
            "url": "https://zmeet-1258547067.cos.ap-shanghai.myqcloud.com/test/verify/1006_20241223_194521_user_audio_0000.wav"
        },
        "en": {
            "file": "/data/Music/youtube/amazon_ceo_60s.wav",
            "url": "https://zmeet-1258547067.cos.ap-shanghai.myqcloud.com/test/amazon_ceo_60s.wav"
        },
        "ru": {
            "file": "/data/Music/russian/russian1-60s.wav",
            "url": "https://zmeet-1258547067.cos.ap-shanghai.myqcloud.com/test/russian1-60s.wav"
        }
    }
    
    APP_ID = "lianxintest2"
    APP_SECRET = "b7c02cd9-8ebe-4d24-a3b1-f094783b651a" 