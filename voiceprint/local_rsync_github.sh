#!/bin/bash
# 创建一个排除规则文件，每行一个规则
echo node_modules > exclude.txt
echo .next >> exclude.txt
echo __pycache__ >> exclude.txt
#echo chroma.db >> exclude.txt
#echo test.db >> exclude.txt
#echo .env >> exclude.txt
echo .git >> exclude.txt
echo .env >> exclude.txt
echo docker-compose.yaml >> exclude.txt
echo media_files >> exclude.txt
rsync -avzP ./ /root/gitlab/github/asr-sdk-v2/voiceprint/  --exclude-from='exclude.txt'
rsync -avzP ./ /root/gitlab/github/asr-sdk-v2/voiceprint/  --exclude-from='exclude.txt'
