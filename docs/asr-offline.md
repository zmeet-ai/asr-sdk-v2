## 录音文件识别请求

### 1. 接口描述

接口请求域名： 
- 创建任务：https://asr-pre.abcpen.com:8443/v2/asr/long/create
- 查询任务：https://asr-pre.abcpen.com:8443/v2/asr/long/query
- 本接口可对较长的录音文件进行识别。
- 接口默认限频：20次/秒。此处仅限制任务提交频次，与识别结果返回时效无关
- 返回时效：异步回调，非实时返回。最长3小时返回识别结果，**大多数情况下，1小时的音频1-3分钟即可完成识别**。请注意：上述返回时长不含音频下载时延，且30分钟内发送超过1000小时录音或2万条任务的情况除外
- 媒体文件格式：**支持几乎所有音视频文件格式**，如mp4, avi, mkv, mov, wmv, flv, webm, mpeg, mpg, h264, hevc, wav、mp3、m4a、flv、mp4、wma、3gp、amr、aac、ogg-opus、flac
- 支持语言：[支持100种国家语言](https://github.com/zmeet-ai/asr-sdk-v2/blob/main/docs/country_code.md)
-  音频提交方式：本接口支持**音频 URL**。推荐使用[阿里云对象存储OSS](https://www.aliyun.com/product/oss?spm=5176.28508143.J_4VYgf18xNlTAyFFbOuOQe.60.e939154aMOdAFn) 、[亚马逊S3](about:blank)和 [腾讯云COS](https://cloud.tencent.com/document/product/436/38484) 等对象存储来存储、生成URL并提交任务，存储桶权限需要设置公有读私有写，或URL设置外部可访问
-  音频限制：音频 URL 时长不能大于5小时，文件大小不超过1GB；本地音频文件不能大于5MB
-  如何获取识别结果：支持**回调或轮询**的方式获取结果，具体请参考 [录音文件识别结果查询](https://cloud.tencent.com/document/product/1093/37822)
-  识别结果有效时间：在服务端保存7天
-  签名方法参考 [公共参数](https://github.com/zmeet-ai/asr-sdk-v2/blob/main/docs/signature.md) 中签名方法

默认接口请求频率限制：20次/秒。



### 2. 输入参数

以下请求参数列表仅列出了接口请求参数，完整公共参数列表见 [公共请求参数](https://github.com/zmeet-ai/asr-sdk-v2/blob/main/docs/signature.md)。

| 参数名称           | 必选 | 类型    | 描述                                                         | 默认值 |
| :----------------- | :--- | :------ | :----------------------------------------------------------- | ------ |
| pd              | 否   | String  | 通用: general <br/>法律: law <br/>教育: edu <br/>金融: finance <br/>医疗: medical <br/>科技: tech <br/>运营商: isp <br/>政府: gov <br/>电商: ecom <br/>军事: mil <br/>企业: com <br/>生活: life <br/>汽车: car<br/>游戏: game<br/>历史: history<br/>互联网: com<br/>娱乐: amuse<br/> | general |
| input_audio_url                | 是   | String  | 音频URL的地址（需要公网环境浏览器可下载） 注意： 1. 请确保录音文件时长在5个小时（含）之内，否则可能识别失败； 2. 请保证文件的下载速度，否则可能下载失败 示例值：https://audio.cos.ap-guangzhou.myqcloud.com/example.wav |        |
| callback_url        | 否   | String  | 回调 URL 用户自行搭建的用于接收识别结果的服务URL 回调格式和内容详见：[录音识别回调说明](https://cloud.tencent.com/document/product/1093/52632)  注意： 如果用户使用轮询方式获取识别结果，则无需提交该参数 |        |
| min_speaker_num      | 否   | Integer | 最小发言者数量 **需配合开启说话人分离使用，不开启无效**，取值范围：0-10 0：自动分离（最多分离出20个人）； 1-10：指定人数分离； 默认值为 0 示例值：0 | 0 |
| max_speaker_num      | 否   | Integer | 最大发言者数量 **需配合开启说话人分离使用，不开启无效**，取值范围：0-10 0：自动分离（最多分离出20个人）； 1-10：指定人数分离； 默认值为 0 示例值：0 | 0 |
| language        | 否   | String  | 语言 默认zh |    |
| words_output        | 否   | String  | 是否输出单词 false：不开启；true：开启    ||
| audio_type | 否 | String | asr: 只做语音识别 <br/>asr_sd: 语音识别+说话人区分 <br/>asr_sd_id: 语音识别+说话人区分+说话人识别 <br/>audio_separate: 人声分离 <br/>audio_separate_asr: 语音识别+说话人区分 <br/>audio_separate_asr_sd: 语音识别+说话人区分+人声分离 <br/>audio_separate_asr_sd_id: 语音识别+说话人区分+说话人识别+人声分离 |asr|

### 3. 输出参数

| 参数名称  | 类型                                                         | 描述                                                         |
| :-------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| data      | {"taskId": String} | 录音文件识别的请求返回结果，包含结果查询需要的TaskId         |
| msg | String                                                       | 接口状态信息 |
| code | String                                                       | 状态码：0为成功，-1未完成|

### 4. 示例

#### 输入示例
```python
"""
流程：
1. 创建离线识别任务
2. 根据taskId查询识别任务状态及结果
"""

# 创建离线识别任务
url_create = f"{baseUrl}/v2/asr/long/create"
url_query = f"{baseUrl}/v2/asr/long/query"

headers = {
    "X-App-Key": app_id,
    "X-App-Signature": signature,
    "X-Timestamp": ts,
    "Content-Type": "application/json"
}
json = {
    "sd": "true",
    "input_audio_url": "https://zos.abcpen.com/tts/zmeet/20221023/b6a2c7ac-52c8-11ed-961e-00155dc6cbed.mp3",
    "language": "zh"
}
response = requests.post(url_create, headers=headers, data=json)
response_json = json.loads(response.text)

# 查询任务
query_task_body = {"task_id": response_json["data"]["task_id"]}
query_response = requests.post(url_query, headers=headers, data=query_task_body)
```

#### 创建离线识别任务返回
```json
{
    "code": "0",
    "data": {
        "task_id": "f591ce70-900b-42c4-87ca-53a43dd31f52"
    },
    "msg": "success"
}
```

#### 查询识别任务返回
```json
{"code": "0", "data": {"data": {"speechResult": {"onebest": "除常规的宠物食品，宠物用具外，宠物殡葬，宠物医疗，宠物保险，宠物服务，线下门店等在外界看来颇为小众的领域，也陆续拿到动辄上千万甚至过亿的投资。近两年，我国一人户家庭数超1.25亿，占比超25%。 2021年，我国饲养猫狗的人群超6800万，其中有近一半 是90后宠物主。当传统家庭结构发生变化，越来越多年轻人把情感倾注到宠物身上，宠物从单纯的陪伴者晋升为亲密家人，而这些毛孩子们也像人类幼崽一样，有着吃喝拉撒睡，医疗，托管，保险等各种需求，愿意为之付费的宠物主们就这样浇灌出一个千亿消费市场。", 
"duration": 53928, "detail": [{"sentences": "除常规的宠物食品，", "wordBg": "320", "wordEd": "2320", "speakerId": "1"}, 
{"sentences": "宠物用具外，", "wordBg": "2320", "wordEd": "3720", "speakerId": "1"}, 
{"sentences": "宠物殡葬，", "wordBg": "3720", "wordEd": "4840", "speakerId": "1"}, 
{"sentences": "宠物医疗，", "wordBg": "4840", "wordEd": "6080", "speakerId": "1"}, 
{"sentences": " 宠物保险，", "wordBg": "6080", "wordEd": "7280", "speakerId": "1"}, 
{"sentences": "宠物服务，", "wordBg": "7280", "wordEd": "8000", "speakerId": "1"}, 
{"sentences": "线下门店等在外界看来颇为小众的领域，", "wordBg": "8000", "wordEd": "11750", "speakerId": "1"}, 
{"sentences": "也陆续拿到动辄上千万甚至过亿的投资。", "wordBg": "11750", "wordEd": "14930", "speakerId": "0"}, 
{"sentences": "近两年，", "wordBg": "15420", "wordEd": "16460", "speakerId": "0"}, 
{"sentences": "我国一人户家庭数超1.25亿，", "wordBg": "16460", "wordEd": "20340", "speakerId": "0"}, 
{"sentences": "占比超25%。", "wordBg": "20340", "wordEd": "22300", "speakerId": "0"}, 
{"sentences": "2021年，", "wordBg": "22300", "wordEd": "23060", "speakerId": "0"}, 
{"sentences": "我国饲养猫狗的人群超6800万，", "wordBg": "23060", "wordEd": "26740", "speakerId": "0"}, 
{"sentences": "其中有近一半是90后宠物主。", "wordBg": "26740", "wordEd": "29200", "speakerId": "0"}, 
{"sentences": "当传统家庭结构发生变化，", "wordBg": "29700", "wordEd": "32300", "speakerId": "0"}, 
{"sentences": "越来越多年轻人把情感倾注到宠物身上，", "wordBg": "32300", "wordEd": "36100", "speakerId": "0"}, 
{"sentences": "宠物从单纯的陪伴者晋升为亲密家人，", "wordBg": "36100", "wordEd": "39780", "speakerId": "0"}, 
{"sentences": "而这些毛孩子们也像人类幼崽一样，", "wordBg": "39780", "wordEd": "42640", "speakerId": "0"}, 
{"sentences": "有着吃喝拉撒睡，", "wordBg": "43070", "wordEd": "44870", "speakerId": "0"}, 
{"sentences": "医疗，", "wordBg": "44870", "wordEd": "45790", "speakerId": "0"}, 
{"sentences": "托管，", "wordBg": "45790", "wordEd": "46510", "speakerId": "1"}, 
{"sentences": "保险等各种需求，", "wordBg": "46510", "wordEd": "48270", "speakerId": "1"}, 
{"sentences": "愿意为之付费的宠物主们就这样浇灌出一个千亿消费市场。", "wordBg": "48270", "wordEd": "53010", "speakerId": "0"}]}}, 
"task_id": "cbaf7296-9390-42ae-9163-b986e53bd32e", "spk_id_text": "", "audio_denoise_url": "", 
"status": {"spk_id_status": 0, "denoise_status": 0, "asr_spk_status": 0}}, "msg": "success"}
```