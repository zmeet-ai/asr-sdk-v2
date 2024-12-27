# 直接运行jar包
## 运行ASR识别
java -jar realtime_asr.jar asr /path/to/audio.wav

## 注册声纹
java -jar realtime_asr.jar register /path/to/audio.wav speaker_name

## 搜索声纹
java -jar realtime_asr.jar search /path/to/audio.wav

## 删除所有声纹
java -jar realtime_asr.jar delete-all

# 运行run.sh
```bash
# 运行ASR识别
./run.sh run asr /path/to/audio.wav

# 注册声纹
./run.sh run register /path/to/audio.wav speaker_name

# 搜索声纹
./run.sh run search /path/to/audio.wav

# 删除所有声纹
./run.sh run delete-all

# 清理、编译、打包并运行（例如ASR模式）
./run.sh all asr /path/to/audio.wav
```
