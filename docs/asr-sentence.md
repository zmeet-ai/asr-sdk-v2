## 一句话语音识别

## 1. 接口描述

接口请求域名： https://asr-pre.abcpen.com:8443/asr/v2/sentence 。

本接口用于对60秒之内的短音频文件进行识别。
- 支持中文普通话、英语,中文,德语,西班牙语,俄语,韩语,法语,日语,葡萄牙语,土耳其语,波兰语,加泰罗尼亚语,荷兰语,阿拉伯语,瑞典语,意大利语,印度尼西亚语,印地语,芬兰语,越南语,希伯来语,乌克兰语,希腊语,马来语,捷克语,罗马尼亚语,丹麦语,匈牙利语,泰米尔语,挪威语,泰语,乌尔都语,克罗地亚语,保加利亚语,立陶宛语,拉丁语,毛利语,马拉雅拉姆语,威尔士语,斯洛伐克语,泰卢固语,波斯语,拉脱维亚语,孟加拉语,塞尔维亚语,阿塞拜疆语,斯洛文尼亚语,卡纳达语,爱沙尼亚语,马其顿语,布列塔尼语,巴斯克语,冰岛语,亚美尼亚语,尼泊尔语,蒙古语,波斯尼亚语,哈萨克语,阿尔巴尼亚语,斯瓦希里语,加利西亚语,马拉地语,旁遮普语,僧伽罗语,高棉语,绍纳语,约鲁巴语,索马里语,南非荷兰语,奥克语,格鲁吉亚语,白俄罗斯语,塔吉克语,信德语,古吉拉特语,阿姆哈拉语,意第绪语,老挝语,乌兹别克语,法罗语,海地克里奥尔语,普什图语,土库曼语,新挪威语,马耳他语,梵语,卢森堡语,缅甸语,藏语,他加禄语,马尔加什语,阿萨姆语,塔塔尔语,夏威夷语,林加拉语,豪萨语,巴什基尔语,爪哇语,巽他语,粤语、上海话、四川话、武汉话、贵阳话、昆明话、西安话、郑州话、太原话、兰州话、银川话、西宁话、南京话、合肥话、南昌话、长沙话、苏州话、杭州话、济南话、天津话、石家庄话、黑龙江话、吉林话、辽宁话。
- 支持本地语音文件上传和语音URL上传两种请求方式，音频时长不能超过60s，音频文件大小不能超过3MB。
- 音频格式支持wav、pcm、ogg-opus、speex、silk、mp3、m4a、aac。
- 请求方法为 HTTP POST , Content-Type为"application/json; charset=utf-8"
- 签名方法参考 [公共参数](https://github.com/zmeet-ai/asr-sdk-v2/blob/main/docs/signature.md) 中签名方法。

​         

## 2. 输入参数

以下请求参数列表仅列出了接口请求参数，完整公共参数列表见 [公共请求参数](https://github.com/zmeet-ai/asr-sdk-v2/blob/main/docs/signature.md)。

| 参数名称         | 必选 | 类型    | 描述                                                         |
| ---------------- | ---- | ------- | ------------------------------------------------------------ |
| audio_url        | 否   | String  | 语音的URL地址，需要公网环境浏览器可下载。音频时长不能超过60s，音频文件大小不能超过3MB。**注意 audio_url和audio_file只能二选一，不能两者都设置，也不能两者都不设置**。 示例值：http://test.voice.com/test.wav |
| punc             | 否   | Integer | 是否显示标点符号（目前支持中文普通话引擎）。 0：不显示，1：显示标点符号。默认值为 1。 示例值：1 |
| language        | 否   | String  | 语言 默认zh |    |

### 输入示例
```py
url = f"{baseUrl}/asr/v2/sentence"
headers = {
    "X-App-Key": app_id,
    "X-App-Signature": signature,
    "X-Timestamp": ts,
    "Content-Type": "application/json"
}
json = {
    "punc": "true",
    "audio_url": "https://zos.abcpen.com/tts/zmeet/20221023/b6a2c7ac-52c8-11ed-961e-00155dc6cbed.mp3",
    "language": "zh"
}
requests.post(url, headers=headers, data=json)
```

## 3. 输出参数

| 参数名称  | 类型                                                         | 描述                                                         |
| --------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Result    | String                                                       | 识别结果。 示例值：测试输出结果                              |
| duration  | Integer                                                      | 请求的音频时长，单位为ms 示例值：1500                        |
| WordSize  | Integer                                                      | 词时间戳列表的长度 注意：此字段可能返回 null，表示取不到有效值。 示例值：4 |
| WordList  | Array of [SentenceWord](https://cloud.tencent.com/document/api/1093/37824#SentenceWord) | 词时间戳列表 注意：此字段可能返回 null，表示取不到有效值。 示例值：array |
| RequestId | String                                                       | 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。 |

## 4. 返回示例
```json
 {"code":"0","data":{"asr":"hello：hello，大家好，晚上都来了啊？大家来了没有？晚上好，晚上好！晚上好！对不起，对不起！稍稍迟到一分钟，一分钟，因为在整理发型，整理耳钉，每天每部！hello：a！三零！hello ：大柔，看到你了，这个晚上好的呀！每次一开播了，以后，就是急急忙忙，急急忙忙的，但是呢，还是希望大家就是能够在这个时候，不要失望，我们稍微迟到三十秒钟，钟会会火！其实一会会儿，先给大家抽个奖，好不好？废话不多 说，先来抽抽奖，给大家抽，分享奖，好，可以，每分奖给大家抽一个，今晚会有产品品吧，而且属属于很多人，在我们直播间会定期回购的，我觉得怎么脸看起来这么奇怪啊？在镜头里面，第一次喊你名字，因为你今天是第一名！第一 名：亲吻鱼：来，我们每天可以给，给，给！大家，就点几个名字，好不好？大：是呢，来，来，眼熟一下，看到你们了！hello：hello：大家晚上好！抽个烧饭的牛排吧！好！好！不好？每个家抽六盒，六盒，六盒。"},"msg":"success"}
```

