
## 接口变动
从2024年起，主路径接口发生如下变动
### 语音识别接口(在线和离线)
```json
/v1/asr 修改为 /asr/v1
/v2/asr 修改为 /asr/v2
```
### nlp接口
```json
/v2/nlp 修改为  /nlp/v2
```

### 给天翼云的鉴权接口
```json
/v2/auth 修改为 /auth/v2
```

### 说话人分离接口
```
/v1/asr/sd 和 /v2/asr/sd 开通的api路径 统一合并到 /asr/v2/long/create
```