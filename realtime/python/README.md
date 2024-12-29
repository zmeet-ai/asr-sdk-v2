## 安装使用说明
* SDK仅支持Python3，暂不支持Python2。
* 安装依赖库：pip install -r requirements.txt
* 可使用conda环境，安装命令：conda create -n asr python=3.10

## 项目启动前先配置 .env
* 在项目根目录下更新 .env 文件

## 实时语音识别
* 运行脚本：python auto_test_asr_v2.py
* 具体参数帮助指引：python auto_test_asr_v2.py --help       
```bash
usage: auto_test_asr_v2.py [-h] [--mode {typewriter,json}] [--asr_type {sentence,word}] [--audio_file AUDIO_FILE]

ASR Client

options:
  -h, --help            show this help message and exit
  --mode {typewriter,json}
                        Output mode: typewriter (default) or json
  --asr_type {sentence,word}
                        ASR recognition mode: sentence (default) or word
  --audio_file AUDIO_FILE
                        Path to the audio file (default: ../dataset/asr/3-1-60s.wav)
```

## 声纹识别
* 运行脚本：python auto_test_speaker_id.py 
* 声纹
    * 声纹注册，选择在安静的环境下进行，否则会影响识别效果；录制16k采样率，16bit量化，单声道，wav格式，文件名格式为：speaker_name.wav
        * 录制的语音时长不超过5分钟。