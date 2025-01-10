# 一句话语音识别API文档

## 接口说明

一句话语音识别（Sentence ASR）基于深度全序列卷积神经网络框架，支持上传音频文件或音频URL进行语音识别。该接口适用于短音频的快速识别场景，支持中文普通话、英语等多语种识别。

## 接口规范

| 内容     | 说明                                                         |
| :------- | :----------------------------------------------------------- |
| 请求协议 | HTTPS                                                         |
| 请求地址 | https://audio.abcpen.com/sentence/v2/sentence                |
| 接口鉴权 | 签名机制，详见 [签名生成](#签名生成)                         |
| 响应格式 | 统一采用JSON格式                                             |
| 开发语言 | 任意，支持所有可发起HTTP请求的开发语言                       |
| 音频格式 | 支持wav、mp3、pcm等常见音频格式                              |
| 音频要求 | 采样率16kHz、位长16bit、单声道                               |
| 音频时长 | 建议60秒以内                                                 |

## 请求参数

### 请求头参数

| 参数名           | 类型   | 必须 | 说明                                     |
| :-------------- | :----- | :--- | :--------------------------------------- |
| X-App-Key       | string | 是   | 启真开放平台应用ID                       |
| X-App-Signature | string | 是   | 签名字符串                               |
| X-Timestamp     | string | 是   | 当前时间戳，单位：秒                     |

### 请求体参数

支持Form表单和JSON两种格式：

#### Form表单格式

| 参数名              | 类型    | 必须 | 说明                                     |
| :----------------- | :------ | :--- | :--------------------------------------- |
| audio_file         | file    | 否   | 音频文件，与audio_url二选一               |
| audio_url          | string  | 否   | 音频URL，与audio_file二选一               |
| language           | string  | 否   | 识别语言，支持zh(中文)、en(英文)等，默认zh |
| fast               | boolean | 否   | 是否使用快速模式，默认false               |
| vocab_id           | string  | 否   | 热词词表ID                               |
| voiceprint_enabled | boolean | 否   | 是否启用声纹识别，默认false              |
| voiceprint_org_id  | string  | 否   | 声纹识别组织ID                           |
| voiceprint_tag_id  | string  | 否   | 声纹识别标签ID                           |

#### JSON格式

需设置Content-Type为application/json，请求体示例：

```json
{
    "audio_file": "base64编码的音频数据",
    "audio_url": "音频文件URL",
    "language": "zh",
    "fast": false,
    "vocab_id": "热词ID",
    "voiceprint_enabled": false,
    "voiceprint_org_id": "声纹组织ID",
    "voiceprint_tag_id": "声纹标签ID"
}
```

## 响应参数

```json
{
    "code": "0",
    "msg": "success",
    "data": {
        "asr": "识别的文本内容",
        "speaker": "说话人名称(启用声纹时返回)"
    }
}
```

| 参数名   | 类型   | 说明                                          |
| :------- | :----- | :-------------------------------------------- |
| code     | string | 返回码，0表示成功                             |
| msg      | string | 返回信息                                      |
| data     | object | 返回数据                                      |
| asr      | string | 识别的文本内容                                |
| speaker  | string | 说话人名称，未启用声纹或未识别到时返回"未知"   |

## 错误码

| 错误码 | 说明                           |
| :----- | :----------------------------- |
| 0      | 成功                           |
| 400    | 请求参数错误                   |
| 401    | 认证失败                       |
| 500    | 服务器内部错误                 |

## 签名生成

1. 获取当前时间戳ts（单位：秒）
2. 拼接app_id和ts生成字符串tt
3. 计算tt的MD5值得到base_string
4. 使用app_secret对base_string进行HMAC-SHA1加密
5. 将加密结果进行Base64编码得到最终签名

Python示例代码：
```python
def generate_signature(app_id: str, app_secret: str) -> tuple[str, str]:
    ts = str(int(time.time()))
    tt = (app_id + ts).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(tt)
    base_string = md5.hexdigest().encode("utf-8")
    
    api_key = app_secret.encode("utf-8")
    signature = hmac.new(api_key, base_string, hashlib.sha1).digest()
    signature = base64.b64encode(signature).decode("utf-8")
    
    return signature, ts
```

## 使用示例

### Python示例

```python
import requests
import base64

def test_sentence_asr():
    url = "https://audio.abcpen.com/sentence/v2/sentence"
    
    # 生成签名
    signature, ts = generate_signature(app_id, app_secret)
    
    headers = {
        "X-App-Key": app_id,
        "X-App-Signature": signature,
        "X-Timestamp": ts
    }
    
    # 使用音频文件
    with open("test.wav", "rb") as f:
        files = {"audio_file": f}
        data = {
            "language": "zh",
            "fast": True
        }
        response = requests.post(url, headers=headers, files=files, data=data)
    
    # 使用音频URL
    data = {
        "audio_url": "https://example.com/test.wav",
        "language": "zh",
        "fast": True
    }
    response = requests.post(url, headers=headers, data=data)
    
    result = response.json()
    print(f"识别结果: {result['data']['asr']}")
```

## 常见问题

### 支持哪些语言？
> 目前主要支持中文普通话、英语，其他语种请联系商务。

### 支持哪些音频格式？
> 支持wav、mp3、pcm等常见音频格式，建议使用采样率16kHz、位长16bit的单声道音频以获得最佳识别效果。

### 音频时长有什么限制？
> 建议音频时长在60秒以内。如需处理较长音频，建议使用实时语音转写接口。

### 如何使用声纹识别功能？
> 1. 设置voiceprint_enabled为true
> 2. 提供voiceprint_org_id和voiceprint_tag_id
> 3. 确保已完成声纹注册
> 4. 识别结果会返回说话人信息

### 如何提升识别准确率？
> 1. 使用优质音频输入
> 2. 合理使用热词功能
> 3. 选择合适的语言参数
> 4. 避免复杂的背景噪音 