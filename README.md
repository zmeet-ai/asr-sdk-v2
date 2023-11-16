# 实时语音转写与同声传译API文档

# 一、语音识别优势

* 支持超过100个国家语言的实时同声传译，同步输出和客户母语对应的实时同传翻译文本和语音合成数据
* **业界领先的声纹识别，返回结果字段中精准识别说话人ID**
* **庞大的声纹数据库，海量音视频文件中毫秒级返回说话人的片段音视频信息**
* **业界领先的降噪算法，返回的音视频文件，可包含降噪后的清晰语音**
* **业界领先的高精准中英文等语音识别算法**

# 二、实时语音转写API文档

## 1、接口说明

实时语音转写（Real-time ASR）基于深度全序列卷积神经网络框架，通过 WebSocket 协议，建立应用与语言转写核心引擎的长连接，开发者可实现将连续的音频流内容，实时识别返回对应的文字流内容。
支持的音频格式： 采样率为16K，采样深度为16bit的pcm_s16le单声道音频

实时语言转写基本兼容科大讯飞接口，同时做了大量简化。


## 2、接口Demo

参照git代码中的sdk实例代码。

## 3、接口参数规范

集成实时语音转写API时，需按照以下要求。

| 内容     | 说明                                                         |
| :------- | ------------------------------------------------------------ |
| 请求协议 | wss                                                          |
| 请求地址 | wss: //asr-prod.abcpen.com/v2/asr/ws?{请求参数} *注：服务器IP不固定，为保证您的接口稳定，请勿通过指定IP的方式调用接口，使用域名方式调用* |
| 接口鉴权 | 签名机制，详见 [signa生成](#signa生成)                       |
| 响应格式 | 统一采用JSON格式                                             |
| 开发语言 | 任意，只要可以向笔声云服务发起WebSocket请求的均可            |
| 音频属性 | 采样率16k、位长16bit、单声道                                 |
| 音频格式 | pcm                                                          |
| 数据发送 | 建议音频流每200ms发送6400字节                                |
| 语言种类 | 中文普通话、中英混合识别、英文；俄罗斯语、阿拉巴语、法语、德语等100多种语言的语音识别另行提供。 |


## 4、接口调用流程

实时语音转写接口调用包括两个阶段：握手阶段和实时通信阶段。

### （1）、握手阶段

接口地址

```bash
wss://asr-prod.abcpen.com/v2/asr/ws?{请求参数}
```

参数格式

```text
key1=value1&key2=value2…（key和value都需要进行urlencode）
```

参数说明

| 参数              | 类型   | 必须 | 说明                                                         | 示例                                                         |
| :---------------- | :----- | :--- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| appid             | string | 是   | 笔声开放平台应用ID                                           | 595f23df                                                     |
| ts                | string | 是   | 当前时间戳，从1970年1月1日0点0分0秒开始到现在的秒数          | 1512041814                                                   |
| signa             | string | 是   | 加密数字签名（基于HMACSHA1算法）                             | IrrzsJeOFk1NGfJHW6SkHUoN9CU=                                 |
| trans_mode        | string | 否   | 为“1”，启动同声翻译，这时必须设置目标语言（target_lang); 为“0”， 不启动同声翻译 | 1                                                            |
| source_lang       | string | 否   | 实时语音转写语种，也就是源语言；不传自动识别                 | 语种类型：中文、中英混合识别：cn；<br/>英文："en" <br/>德文："de" <br/>法语："fr" <br/> 西班牙语："es" <br/>意大利："it" <br/>俄罗斯："ru" <br/> 日语 "ja" <br/>韩国 "ko" <br/>更多语言参考本文附录 |
| target_lang       | string | 否   | 启动实时翻译的时候，设置的目标语言                           | 语种类型：中文、中英混合识别：cn；<br/>英文："en" <br/>德文："de" <br/>法语："fr" <br/> 西班牙语："es" <br/>意大利："it" <br/>俄罗斯："ru" <br/> 日语 "ja" <br/>韩国 "ko" <br/>更多语言参考本文附录 |
| punc              | string | 否   | 标点过滤控制，默认返回标点，punc=0会过滤结果中的标点         | 1                                                            |
| speaker_number    | string | 否   | 发音人个数，可选值：0-10，0表示盲分                          | 默认：2（适用通话时两个人对话的场景）                        |
| scene             | string | 否   | 垂直领域个性化参数: <br/>法院: court <br/>教育: edu <br/>金融: finance <br/>医疗: medical <br/>科技: tech <br/>运营商: isp <br/>政府: gov <br/>电商: ecom <br/>军事: mil <br/>企业: com <br/>生活: life <br/>汽车: car | 设置示例：scene="edu" 参数scene为非必须设置，不设置参数默认为通用 |
| audio_sample_rate | string | 否   | 音频采样率，有"8000", "16000"，分别代表采样率是8K和16K，默认是“16000” | “16000”                                                      |
| asr_type          | string | 否   | 识别结果输出类型，0，不输出逐字和逐句结果；1，输出逐字和逐句结果，默认为0不输出 | “0”                                                          |

（2）、实时变更同声传译参数, 可在实时识别的时候传输下面的json字符串，以实时变更输出结果，如是否启动同声传译，启动同声传译时候的目标语言；是否对识别结果打标点符号；识别场景切换等。

 ```json
                         //传输该控制命令的时候，将下面的json数据编码成字符串传输（不是二进制数据）
                         {
                             "translate": {
                                 "src_lang": "zh",
                                 "tgt_lang": "en",
                                 "enabled": 1
                             },
                             "punc":{
                                 "enabled": 1
                             },
                             "scene": "court"
                         }
 ```

实时变更参数说明：

* 语言参数
  * src_lang:  源语言，如“zh', "de"等；如输入空格字符串表示自动识别源语言
  * tgt_lang: 目标语言，如”de", "ja" 等
  * 常见翻译语种：控制把源语言转换成什么类型的语言；<br/>中文：cn<br/>英文：en<br/>日语：ja<br/>韩语：ko<br/>俄语：ru<br/>法语：fr<br/>西班牙语：es<br/>意大利：vi<br/>
* enabled： 是否打开同声传译，1表示打开，0表示关闭同声传译

### （2）、signa生成



### （3）、返回值

结果格式为json，字段说明如下：

| 参数   | 类型   | 说明                              |
| :----- | :----- | :-------------------------------- |
| action | string | 结果标识，result:结果，error:异常 |
| code   | string | 结果码(具体见[错误码](#错误码))   |
| data   | string | 结果数据                          |
| desc   | string | 描述                              |
| sid    | string | 会话ID                            |

其中sid字段主要用于DEBUG追查问题，如果出现问题，可以提供sid帮助确认问题。

> 成功

```json
{'action': 'result', 'code': '0', 'data': {}, 'desc': 'success', 'sid': '0', 'asr': '', 'translate': {}}
```

> 失败

```json
	{
	    "action":"error",
		"code":"10110",
		"data":"",
		"desc":"invalid authorization|illegal signa",
		"sid":"0"
	}
```

### （4）、实时通信阶段

握手成功后，进入实时通信阶段，此时客户端的主动操作有两种：上传数据和上传结束标识，被动操作有两种：接收转写结果和错误

### （5）、上传数据

在实时转写过程中，客户端不断构造binary message发送到服务端，内容是音频的二进制数据。此操作的频率影响到文字结果展现的实时性。

注意：

1.建议音频流每200ms发送6400字节，发送过快可能导致引擎出错； 2.音频发送间隔超时时间为15秒，超时服务端报错并主动断开连接。

### （6）、上传结束标志

音频数据上传完成后，客户端需发送一个特殊的binary message到服务端作为结束标识，内容是：

```json
 	{"end" : true}
```

###  （7）、接收转写结果

交互过程中，服务端不断返回 text message （转写结果） 到客户端。当所有结果发送完毕后，服务端断开连接，交互结束。

* 结果示例：

```json
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '7688', 'ed': '8691', 'type': '1', 'rt': [{'w': '俄罗斯方块儿。', 'translate': {'english': 'Russian squares.'}, 'ws': [{'wb': '7688', 'we': '7796', 'cw': [{'w': '俄', 'wp': 1}]}, {'wb': '7796', 'we': '7904', 'cw': [{'w': '罗', 'wp': 1}]}, {'wb': '8135', 'we': '8296', 'cw': [{'w': '斯', 'wp': 1}]}, {'wb': '8360', 'we': '8520', 'cw': [{'w': '方', 'wp': 1}]}, {'wb': '8583', 'we': '8691', 'cw': [{'w': '块', 'wp': 1}]}, {'wb': '8691', 'we': '8800', 'cw': [{'w': '儿', 'wp': 1}]}]}]}}, 'seg_id': 4}, 'desc': 'success', 'sid': 'a0a44031-ac75-4929-9773-2a6bd46450e7', 'asr': '俄罗斯方块儿。', 'translate': {'english': 'Russian squares.'}}
```

* 转写结果字段说明如下：

| 字段      | 含义                                                         | 描述                                 |
| :-------- | :----------------------------------------------------------- | :----------------------------------- |
| bg        | 句子在整段语音中的开始时间，单位毫秒(ms)                     | 中间结果的bg为准确值                 |
| ed        | 句子在整段语音中的结束时间，单位毫秒(ms)                     | 中间结果的ed为0                      |
| w         | 语音识别结果                                                 | **这是实时识别的结果**               |
| asr       | 语音识别结果（为方便调用，我们同时将识别结果asr放在返回结构的最外层） | **这是实时识别的结果**               |
| translate | 同声传译的结果（为方便调用，我们同时将识别结果asr放在返回结构的最外层） | **这是实时同声传译的结果**           |
| wp        | 词标识                                                       | n-普通词；s-顺滑词（语气词）；p-标点 |
| wb        | 词在本句中的开始时间，单位是帧，1帧=10ms 即词在整段语音中的开始时间为(bg+wb*10)ms |                                      |
| we        | 词在本句中的结束时间，单位是帧，1帧=10ms 即词在整段语音中的结束时间为(bg+we*10)ms |                                      |
| type      | 结果类型标识                                                 | 0-最终结果；1-中间结果               |
| seg_id    | 转写结果序号                                                 | 从0开始                              |

### （8）、接收错误信息

交互过程中，在服务端出现异常而中断服务时（如会话超时），会将异常信息以 text message 形式返回给客户端并关闭连接。

### （9）、 实时变更指令，实现语言的切换，或者场景的切换

变更源语言和目标语言, 和变更场景，统一使用下述指令，实时发送到现有的已有的websocket链接上（和语音数据的二进制数据不同）

{"config": { "lang": {"source_lang": "zh", "target_lang": "en"}}, "scene": "law"}

* lang字典表示源语言和目标语言切换（有lang字典的时候，source_lang和target_lang必须同时存在），scene表示场景切换； 
* lang和scene两者或的存在，也就是：
  * 有lang，无scene
  * 无lang，有scene
  * 有lang，有scene

## 5、白名单

在调用该业务接口时

- 若关闭IP白名单，接口认为IP不限，不会校验IP。
- 若打开IP白名单，则服务端会检查调用方IP是否在笔声开放平台配置的IP白名单中，对于没有配置到白名单中的IP发来的请求，服务端会拒绝服务。

IP白名单规则

- 不同Appid的不同服务都需要分别设置IP白名单；
- IP白名单需设置为外网IP，请勿设置局域网IP。
- 如果服务器返回结果如下所示(illegal client_ip)，则表示由于未配置IP白名单或配置有误，服务端拒绝服务。

```json
{
	"action": "error",
	"code": "10105",
	"data": "",
	"desc": "illegal access|illegal client_ip: xx.xx.xx.xx",
	"sid": "rta..."
}
```

## 6、错误码

| 错误码 | 描述                                                         | 说明                     | 处理方式                                                    |
| :----- | :----------------------------------------------------------- | :----------------------- | :---------------------------------------------------------- |
| 0      | success                                                      | 成功                     |                                                             |
| -1     | in progress                                                  | 识别中                   | 请继续重试                                                  |
| -2     | audio encode error                                           | 音频编码错误             | 请编码成正确的格式，再提交请求                              |
| 10105  | illegal access                                               | 没有权限                 | 检查apiKey，ip，ts等授权参数是否正确                        |
| 10106  | invalid parameter                                            | 无效参数                 | 上传必要的参数， 检查参数格式以及编码                       |
| 10107  | illegal parameter                                            | 非法参数值               | 检查参数值是否超过范围或不符合要求                          |
| 10109  | audio url is not valid http(s) url                           | audio_url不是http[s]链接 | 长语音识别的时候，audio_url必须是http[s]链接                |
| 10110  | no license                                                   | 无授权许可               | 检查参数值是否超过范围或不符合要求                          |
| 10700  | engine error                                                 | 引擎错误                 | 提供接口返回值，向服务提供商反馈                            |
| 10701  | Audio encode error, only support pcm, aac, mpeg2, opus and flac | 音频编码错误             | 支持pcm, aac, mpeg2, opus 和 flac这几种编码，请选择其中一种 |
| 10702  | Audio sample error, only support 8000、16000、44100 and 48000 Hz | 音频采样率错误           | 支持 8000、16000、44100 和 48000 Hz，请选择其中一种         |
| 10202  | websocket connect error                                      | websocket连接错误        | 检查网络是否正常                                            |
| 10204  | websocket write error                                        | 服务端websocket写错误    | 检查网络是否正常，向服务提供商反馈                          |
| 10205  | websocket read error                                         | 服务端websocket读错误    | 检查网络是否正常，向服务提供商反馈                          |
| 16003  | basic component error                                        | 基础组件异常             | 重试或向服务提供商反馈                                      |
| 10800  | over max connect limit                                       | 超过授权的连接数         | 确认连接数是否超过授权的连接数                              |

## 7、常见问题
#### （1）、 同声传译支持哪些国家的语言。所有语言参数输入的时候，请从下面的对照表中选择相应语言的2位编码，编码值遵从

  [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

我们支持如下国家的语言
```python
LANGUAGES = {
    "en": "英语",
    "zh": "中文",
    "de": "德语",
    "es": "西班牙语",
    "ru": "俄语",
    "ko": "韩语",
    "fr": "法语",
    "ja": "日语",
    "pt": "葡萄牙语",
    "tr": "土耳其语",
    "pl": "波兰语",
    "ca": "加泰罗尼亚语",
    "nl": "荷兰语",
    "ar": "阿拉伯语",
    "sv": "瑞典语",
    "it": "意大利语",
    "id": "印度尼西亚语",
    "hi": "印地语",
    "fi": "芬兰语",
    "vi": "越南语",
    "he": "希伯来语",
    "uk": "乌克兰语",
    "el": "希腊语",
    "ms": "马来语",
    "cs": "捷克语",
    "ro": "罗马尼亚语",
    "da": "丹麦语",
    "hu": "匈牙利语",
    "ta": "泰米尔语",
    "no": "挪威语",
    "th": "泰语",
    "ur": "乌尔都语",
    "hr": "克罗地亚语",
    "bg": "保加利亚语",
    "lt": "立陶宛语",
    "la": "拉丁语",
    "mi": "毛利语",
    "ml": "马拉雅拉姆语",
    "cy": "威尔士语",
    "sk": "斯洛伐克语",
    "te": "泰卢固语",
    "fa": "波斯语",
    "lv": "拉脱维亚语",
    "bn": "孟加拉语",
    "sr": "塞尔维亚语",
    "az": "阿塞拜疆语",
    "sl": "斯洛文尼亚语",
    "kn": "卡纳达语",
    "et": "爱沙尼亚语",
    "mk": "马其顿语",
    "br": "布列塔尼语",
    "eu": "巴斯克语",
    "is": "冰岛语",
    "hy": "亚美尼亚语",
    "ne": "尼泊尔语",
    "mn": "蒙古语",
    "bs": "波斯尼亚语",
    "kk": "哈萨克语",
    "sq": "阿尔巴尼亚语",
    "sw": "斯瓦希里语",
    "gl": "加利西亚语",
    "mr": "马拉地语",
    "pa": "旁遮普语",
    "si": "僧伽罗语",
    "km": "高棉语",
    "sn": "绍纳语",
    "yo": "约鲁巴语",
    "so": "索马里语",
    "af": "南非荷兰语",
    "oc": "奥克语",
    "ka": "格鲁吉亚语",
    "be": "白俄罗斯语",
    "tg": "塔吉克语",
    "sd": "信德语",
    "gu": "古吉拉特语",
    "am": "阿姆哈拉语",
    "yi": "意第绪语",
    "lo": "老挝语",
    "uz": "乌兹别克语",
    "fo": "法罗语",
    "ht": "海地克里奥尔语",
    "ps": "普什图语",
    "tk": "土库曼语",
    "nn": "新挪威语",
    "mt": "马耳他语",
    "sa": "梵语",
    "lb": "卢森堡语",
    "my": "缅甸语",
    "bo": "藏语",
    "tl": "他加禄语",
    "mg": "马尔加什语",
    "as": "阿萨姆语",
    "tt": "塔塔尔语",
    "haw": "夏威夷语",
    "ln": "林加拉语",
    "ha": "豪萨语",
    "ba": "巴什基尔语",
    "jw": "爪哇语",
    "su": "巽他语",
    "yue": "粤语",
}
```
#### (2)、实时语音转写支持什么平台？

> 答：实时转写只支持webapi接口，开放平台“实时语音转写”需要WebSocket接入，针对是有编程基础的开发者用户。如果您是个人用户，不想通过编程方式直接实现语音转写功能，可以去笔声官网，了解语音转写功能的更多详情。

#### （3）、实时语音转写支持什么语言？

> 答：中文普通话、中英混合识别、英文；中英文之外的语音识别请联系商务。

#### （4）支持的音频是什么格式？

> 答：采样率为16K，采样深度为16bit的pcm_s16le音频

#### （5）、实时语音转写支持的音频时长有什么限制？

> 答：实时语音转写可以实时识别持续的音频流，结果是实时返回，音频流长度理论上不做限制，典型的应用场景是大会或者直播的实时字幕。

#### （6）、实时语音转写的分片时长200ms是什么意思？

> 答：可以理解为上传的间隔为200ms，建议音频流每200ms向服务器发送6400字节，发过快可能导致引擎出错，音频发送间隔超时时间为15s，超时服务端报错并主动断开连接。

#### （7）、实时语音转写支不支持离线？

> 答：这个问题有点矛盾；我们有离线识别的api，请使用离线asr api完成请求服务。

#### （8）、实时语音转写如果一次连接使用时长超出了剩余时长怎么办？

> 答：首先为了使业务使用不受影响，如果在连接期间使用时长超出，转写功能并不会立刻停止。本次连接断开后时长可能会出现为负数的情况，请在使用过程中关注时长剩余情况并及时购买时长。
#### 附录：一次完整的同声传译交互过程
```json
{'action': 'started', 'code': '0', 'data': {}, 'desc': 'success', 'sid': '0', 'asr': '', 'translate': {}}
{'action': 'result', 'code': '0', 'data': {'seg_id': 1}, 'desc': 'success', 'sid': '0', 'asr': '', 'translate': {}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '1028', 'type': '1', 'rt': [{'w': '英特', 'translate': {'english': 'Int.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1188', 'cw': [{'w': '特', 'wp': 1}]}]}]}}, 'seg_id': 2}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特', 'translate': {'english': 'Int.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '1136', 'type': '1', 'rt': [{'w': '英特尔', 'translate': {'english': 'Intel.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}]}]}}, 'seg_id': 3}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔', 'translate': {'english': 'Intel.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '1531', 'type': '1', 'rt': [{'w': '英特尔是', 'translate': {'english': 'Intel is...'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}]}]}}, 'seg_id': 4}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是', 'translate': {'english': 'Intel is...'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '2203', 'type': '1', 'rt': [{'w': '英特尔是当之无愧', 'translate': {'english': 'Intel deserves it.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}]}]}}, 'seg_id': 5}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧', 'translate': {'english': 'Intel deserves it.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '2428', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的', 'translate': {'english': 'Intel deserves it.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}]}]}}, 'seg_id': 6}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧 的', 'translate': {'english': 'Intel deserves it.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '2987', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的第一代', 'translate': {'english': 'Intel is the first generation to be deserved.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '2596', 'we': '2732', 'cw': [{'w': '第', 'wp': 1}]}, {'wb': '2732', 'we': '2867', 'cw': [{'w': '一', 'wp': 1}]}, {'wb': '2987', 'we': '3147', 'cw': [{'w': '代', 'wp': 1}]}]}]}}, 'seg_id': 7}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之 无愧的第一代', 'translate': {'english': 'Intel is the first generation to be deserved.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '3212', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的第一代C', 'translate': {'english': 'Intel is the first generation C to be deserved.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '2596', 'we': '2732', 'cw': [{'w': '第', 'wp': 1}]}, {'wb': '2732', 'we': '2867', 'cw': [{'w': '一', 'wp': 1}]}, {'wb': '2987', 'we': '3147', 'cw': [{'w': '代', 'wp': 1}]}, {'wb': '3212', 'we': '3372', 'cw': [{'w': 'C', 'wp': 1}]}]}]}}, 'seg_id': 8}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧的第一代C', 'translate': {'english': 'Intel is the first generation C to be deserved.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '3827', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的第一代CPU制造', 'translate': {'english': 'Intel was made by the first generation of well-deserved CPUs.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '2596', 'we': '2732', 'cw': [{'w': '第', 'wp': 1}]}, {'wb': '2732', 'we': '2867', 'cw': [{'w': '一', 'wp': 1}]}, {'wb': '2987', 'we': '3147', 'cw': [{'w': '代', 'wp': 1}]}, {'wb': '3436', 'we': '3596', 'cw': [{'w': 'CPU', 'wp': 1}]}, {'wb': '3660', 'we': '3820', 'cw': [{'w': '制', 'wp': 1}]}, {'wb': '3827', 'we': '3987', 'cw': [{'w': '造', 'wp': 1}]}]}]}}, 'seg_id': 9}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧的第一代CPU制造', 'translate': {'english': 'Intel was made by the first generation of well-deserved CPUs.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '4052', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的第一代CPU制造商', 'translate': {'english': 'Intel was the first well-deserved CPU manufacturer.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '2596', 'we': '2732', 'cw': [{'w': '第', 'wp': 1}]}, {'wb': '2732', 'we': '2867', 'cw': [{'w': '一', 'wp': 1}]}, {'wb': '2987', 'we': '3147', 'cw': [{'w': '代', 'wp': 1}]}, {'wb': '3436', 'we': '3596', 'cw': [{'w': 'CPU', 'wp': 1}]}, {'wb': '3660', 'we': '3820', 'cw': [{'w': '制', 'wp': 1}]}, {'wb': '3827', 'we': '3987', 'cw': [{'w': '造', 'wp': 1}]}, {'wb': '4052', 'we': '4212', 'cw': [{'w': '商', 'wp': 1}]}]}]}}, 'seg_id': 10}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧的第一代CPU制造商', 'translate': {'english': 'Intel was the first well-deserved CPU manufacturer.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '4052', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的第一代CPU制造商', 'translate': {'english': 'Intel was the first well-deserved CPU manufacturer.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '2596', 'we': '2732', 'cw': [{'w': '第', 'wp': 1}]}, {'wb': '2732', 'we': '2867', 'cw': [{'w': '一', 'wp': 1}]}, {'wb': '2987', 'we': '3147', 'cw': [{'w': '代', 'wp': 1}]}, {'wb': '3436', 'we': '3596', 'cw': [{'w': 'CPU', 'wp': 1}]}, {'wb': '3660', 'we': '3820', 'cw': [{'w': '制', 'wp': 1}]}, {'wb': '3827', 'we': '3987', 'cw': [{'w': '造', 'wp': 1}]}, {'wb': '4052', 'we': '4212', 'cw': [{'w': '商', 'wp': 1}]}]}]}}, 'seg_id': 11}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧的第一代CPU制造商', 'translate': {'english': 'Intel was the first well-deserved CPU manufacturer.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '4947', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的第一代CPU制造商创造了', 'translate': {'english': 'Intel was created by a well-deserved first generation of CPU manufacturers.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '2596', 'we': '2732', 'cw': [{'w': '第', 'wp': 1}]}, {'wb': '2732', 'we': '2867', 'cw': [{'w': '一', 'wp': 1}]}, {'wb': '2987', 'we': '3147', 'cw': [{'w': '代', 'wp': 1}]}, {'wb': '3436', 'we': '3596', 'cw': [{'w': 'CPU', 'wp': 1}]}, {'wb': '3660', 'we': '3820', 'cw': [{'w': '制', 'wp': 1}]}, {'wb': '3827', 'we': '3987', 'cw': [{'w': '造', 'wp': 1}]}, {'wb': '4052', 'we': '4212', 'cw': [{'w': '商', 'wp': 1}]}, {'wb': '4612', 'we': '4772', 'cw': [{'w': '创', 'wp': 1}]}, {'wb': '4780', 'we': '4940', 'cw': [{'w': '造', 'wp': 1}]}, {'wb': '4947', 'we': '5107', 'cw': [{'w': '了', 'wp': 1}]}]}]}}, 'seg_id': 12}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧的第一代CPU制造商创造了', 'translate': {'english': 'Intel was created by a well-deserved first generation of CPU manufacturers.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '5284', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的第一代CPU制造商创造了无数', 'translate': {'english': 'Intel was the first well-deserved CPU manufacturer to create so many.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '2596', 'we': '2732', 'cw': [{'w': '第', 'wp': 1}]}, {'wb': '2732', 'we': '2867', 'cw': [{'w': '一', 'wp': 1}]}, {'wb': '2987', 'we': '3147', 'cw': [{'w': '代', 'wp': 1}]}, {'wb': '3436', 'we': '3596', 'cw': [{'w': 'CPU', 'wp': 1}]}, {'wb': '3660', 'we': '3820', 'cw': [{'w': '制', 'wp': 1}]}, {'wb': '3827', 'we': '3987', 'cw': [{'w': '造', 'wp': 1}]}, {'wb': '4052', 'we': '4212', 'cw': [{'w': '商', 'wp': 1}]}, {'wb': '4612', 'we': '4772', 'cw': [{'w': '创', 'wp': 1}]}, {'wb': '4780', 'we': '4940', 'cw': [{'w': '造', 'wp': 1}]}, {'wb': '4947', 'we': '5107', 'cw': [{'w': '了', 'wp': 1}]}, {'wb': '5116', 'we': '5275', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '5284', 'we': '5444', 'cw': [{'w': '数', 'wp': 1}]}]}]}}, 'seg_id': 13}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧的第一代CPU制造商创造了无数', 'translate': {'english': 'Intel was the first well-deserved CPU manufacturer to create so many.'}}
{'action': 'result', 'code': '0', 'data': {'cn': {'st': {'bg': '860', 'ed': '6124', 'type': '1', 'rt': [{'w': '英特尔是当之无愧的第一代CPU制造商创造了无数的世界纪录。', 'translate': {'english': 'Intel was the first generation of well-deserved CPU manufacturers to create countless world records.'}, 'ws': [{'wb': '860', 'we': '1020', 'cw': [{'w': '英', 'wp': 1}]}, {'wb': '1028', 'we': '1136', 'cw': [{'w': '特', 'wp': 1}]}, {'wb': '1136', 'we': '1244', 'cw': [{'w': '尔', 'wp': 1}]}, {'wb': '1531', 'we': '1691', 'cw': [{'w': '是', 'wp': 1}]}, {'wb': '1700', 'we': '1860', 'cw': [{'w': '当', 'wp': 1}]}, {'wb': '1868', 'we': '2028', 'cw': [{'w': '之', 'wp': 1}]}, {'wb': '2036', 'we': '2196', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '2203', 'we': '2363', 'cw': [{'w': '愧', 'wp': 1}]}, {'wb': '2428', 'we': '2587', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '2596', 'we': '2732', 'cw': [{'w': '第', 'wp': 1}]}, {'wb': '2732', 'we': '2867', 'cw': [{'w': '一', 'wp': 1}]}, {'wb': '2987', 'we': '3147', 'cw': [{'w': '代', 'wp': 1}]}, {'wb': '3436', 'we': '3596', 'cw': [{'w': 'CPU', 'wp': 1}]}, {'wb': '3660', 'we': '3820', 'cw': [{'w': '制', 'wp': 1}]}, {'wb': '3827', 'we': '3987', 'cw': [{'w': '造', 'wp': 1}]}, {'wb': '4052', 'we': '4212', 'cw': [{'w': '商', 'wp': 1}]}, {'wb': '4612', 'we': '4772', 'cw': [{'w': '创', 'wp': 1}]}, {'wb': '4780', 'we': '4940', 'cw': [{'w': '造', 'wp': 1}]}, {'wb': '4947', 'we': '5107', 'cw': [{'w': '了', 'wp': 1}]}, {'wb': '5116', 'we': '5275', 'cw': [{'w': '无', 'wp': 1}]}, {'wb': '5284', 'we': '5444', 'cw': [{'w': '数', 'wp': 1}]}, {'wb': '5452', 'we': '5612', 'cw': [{'w': '的', 'wp': 1}]}, {'wb': '5620', 'we': '5780', 'cw': [{'w': '世', 'wp': 1}]}, {'wb': '5787', 'we': '5947', 'cw': [{'w': '界', 'wp': 1}]}, {'wb': '5955', 'we': '6115', 'cw': [{'w': '纪', 'wp': 1}]}, {'wb': '6124', 'we': '6284', 'cw': [{'w': '录', 'wp': 1}]}]}]}}, 'seg_id': 14}, 'desc': 'success', 'sid': 'cae8bd0f-c5c1-41a5-aae1-db655ff606ee', 'asr': '英特尔是当之无愧的第一代CPU制造商创造了无数的世界纪录。', 'translate': {'english': 'Intel was the first generation of well-deserved CPU manufacturers to create countless world records.'}}
```