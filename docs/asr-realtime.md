# 实时语音转写与同声传译API文档

# 实时语音转写API文档

## 接口说明

实时语音转写（Real-time ASR）基于深度全序列卷积神经网络框架，通过 WebSocket 协议，建立应用与语言转写核心引擎的长连接，开发者可实现将连续的音频流内容，实时识别返回对应的文字流内容。
支持的音频格式： 采样率为16K，采样深度为16bit的**pcm_s16le**单声道音频

## 注意事项

* 如果开启实时声纹识别，因为声纹识别根据计算量不同可能比实时asr识别有滞后，所以客户端不要主动关闭websocket连接
* 服务端做完毕所有实时asr识别和实时声纹识别后，会主动断掉客户端lian'jie


## 接口Demo

参照git代码中的sdk实例代码。

## 接口参数规范

集成实时语音转写API时，需按照以下要求。

| 内容     | 说明                                                         |
| :------- | ------------------------------------------------------------ |
| 请求协议 | wss                                                          |
| 请求地址 | wss://audio.abcpen.com:8443/asr-realtime/v2/ws?{请求参数} ** |
| 接口鉴权 | 签名机制，详见 [signa生成](#signa生成)                       |
| 响应格式 | 统一采用JSON格式                                             |
| 开发语言 | 任意，只要可以向启真云服务发起WebSocket请求的均可            |
| 音频属性 | 采样率16k、位长16bit、单声道(pcm_s16le)                      |
| 音频格式 | pcm                                                          |
| 数据发送 | 建议音频流每200ms发送6400字节                                |


## 接口调用流程

实时语音转写接口调用包括两个阶段：握手阶段和实时通信阶段。

### 握手阶段

接口地址

```bash
wss://audio.abcpen.com:8443/asr-realtime/v2/ws?{请求参数}
```

   

参数格式

```text
key1=value1&key2=value2…（key和value都需要进行urlencode）
```

参数说明

| 参数              | 类型   | 必须 | 说明                                                         | 示例                                                         |
| :---------------- | :----- | :--- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| appid             | string | 是   | 启真开放平台应用ID                                           | 595f23df                                                     |
| ts                | string | 是   | 当前时间戳，从1970年1月1日0点0分0秒开始到现在的秒数          | 1512041814                                                   |
| signa             | string | 是   | 加密数字签名（基于HMACSHA1算法）                             | IrrzsJeOFk1NGfJHW6SkHUoN9CU=                                 |
| voiceprint        | string | 否   | 是否启用实时声纹识别（对返回的每段话做说话人实时识别）； 为1表示启用，为0表示不启用。 默认开启。 | 1                                                            |
| voiceprint_org_id | string | 否   | 声纹识别的组织id，默认为申请app key时候给的application id。 org id + tag id + speaker name组成一个最终确认的说话人身份。 | 默认为申请app key时候给的application id                      |
| voiceprint_tag_id | string |      | 声纹识别的tag id， 默认为申请app key时候给的application id。 org id + tag id + speaker name组成一个最终确认的说话人身份。 | 默认为申请app key时候给的application id                      |
| scene             | string | 否   | 垂直领域个性化参数: <br/>法院: court <br/>教育: edu <br/>金融: finance <br/>医疗: medical <br/>科技: tech <br/>运营商: isp <br/>政府: gov <br/>电商: ecom <br/>军事: mil <br/>企业: com <br/>生活: life <br/>汽车: car | 设置示例：scene="edu" 参数scene为非必须设置，不设置参数默认为通用 |
| asr_type          | string | 否   | 识别结果输出类型，sentence，输出逐句结果；word，输出逐字和逐句结果，默认为word。 | "word"                                                       |
| noise_threshold   | float  | 否   | 噪音参数阈值，默认为0.5，取值范围：[0.3,1]，对于一些音频片段，取值越大，判定为噪音情况越大。取值越小，判定为人声情况越大。<br/>**慎用：可能影响识别效果** | 0.5                                                          |

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
  * 可选国家编码列表有：af, am, ar, as, az, ba, be, bg, bn, bo, br, bs, ca, cs, cy, da, de, el, en, es, et, eu, fa, fi, fo, fr, gl, gu, ha, haw, he, hi, hr, ht, hu, hy, id, is, it, ja, jw, ka, kk, km, kn, ko, la, lb, ln, lo, lt, lv, mg, mi, mk, ml, mn, mr, ms, mt, my, ne, nl, nn, no, oc, pa, pl, ps, pt, ro, ru, sa, sd, si, sk, sl, sn, so, sq, sr, su, sv, sw, ta, te, tg, th, tk, tl, tr, tt, uk, ur, uz, vi, yi, yo, zh
* enabled： 是否打开同声传译，1表示打开，0表示关闭同声传译

### signa生成 

* 参考对应的sdk代码。

### 返回值

结果格式为json，字段说明如下：

| 参数   | 类型   | 说明                                                         |
| :----- | :----- | :----------------------------------------------------------- |
| code   | string | 结果码(具体见 <a href="#错误码">错误码</a> ， 出现错误的时候返回) |
| msg    | string | 结果数据（出现错误的时候返回）                               |
| seg_id | string | 从0开始的语句id，返回的每条语句逐步递增seg_id; 注意只有一句话完整稳定识别后才会递增seg_id, is_final为True， 表示一句话完全稳定识别完毕。 |

其中seg_id字段主要用于DEBUG追查问题，如果出现问题，可以提供sid帮助确认问题。

> 成功

```json
{'rt': [], 'is_final': False, 'seg_id': 0, 'asr': '哈喽', 'translate': ''}
```

> 失败

```json
	{
		"code":"10106",
		"msg":"invalid parameter"
	}
```

### 实时通信阶段

握手成功后，进入实时通信阶段，此时客户端的主动操作有两种：上传数据和上传结束标识，被动操作有两种：接收转写结果和错误

### 上传数据

在实时转写过程中，客户端不断构造binary message发送到服务端，内容是音频的二进制数据。此操作的频率影响到文字结果展现的实时性。

注意：

1.建议音频流每200ms发送6400字节，发送过快可能导致引擎出错； 2.音频发送间隔超时时间为5秒(闲置时间过长)，超时服务端报错并主动断开连接。

### 上传结束标志

音频数据上传完成后，客户端需发送一个特殊的binary message到服务端作为结束标识，内容是：

```json
 	{""} 或者 {"end": true}
```

###  接收转写结果

交互过程中，服务端不断返回 text message （转写结果） 到客户端。当所有结果发送完毕后，服务端断开连接，交互结束。

* 结果示例：

```json
{'rt': [], 'is_final': False, 'seg_id': 0, 'asr': '哈喽', 'translate': ''}
```

* 转写结果字段说明如下：

| 字段      | 含义           | 描述                          |
| :-------- | :------------- | :---------------------------- |
| asr       | 语音识别结果   | **这是实时识别的结果**        |
| translate | 同声传译的结果 | **这是实时同声传译的结果**    |
| is_final  | 结果类型标识   | True-最终结果；False-中间结果 |
| seg_id    | 转写结果序号   | 从0开始                       |

### 接收错误信息

交互过程中，在服务端出现异常而中断服务时（如会话超时），会将异常信息以 text message 形式返回给客户端并关闭连接。

###  实时变更指令，实现语言的切换，或者场景的切换

变更源语言和目标语言, 和变更场景，统一使用下述指令，实时发送到现有的已有的websocket链接上（和语音数据的二进制数据不同）

{"config": { "lang": {"source_lang": "zh", "target_lang": "en"}}, "scene": "law"}

* lang字典表示源语言和目标语言切换（有lang字典的时候，source_lang和target_lang必须同时存在），scene表示场景切换； 
* lang和scene两者或的存在，也就是：
  * 有lang，无scene
  * 无lang，有scene
  * 有lang，有scene

## 白名单

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

## 错误码

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

## 常见问题

#### 实时语音转写支持什么平台？

> 答：实时转写只支持webapi接口，开放平台“实时语音转写”需要WebSocket接入，针对是有编程基础的开发者用户。如果您是个人用户，不想通过编程方式直接实现语音转写功能，可以去笔声官网，了解语音转写功能的更多详情。

#### 实时语音转写支持什么语言？

> 答：中文普通话、中英混合识别、英文；中英文之外的语音识别请联系商务。

#### 支持的音频是什么格式？

> 答：采样率为16K，采样深度为16bit的pcm_s16le音频

#### 实时语音转写支持的音频时长有什么限制？

> 答：实时语音转写可以实时识别持续的音频流，结果是实时返回，音频流长度理论上不做限制，典型的应用场景是大会或者直播的实时字幕。

#### 实时语音转写的分片时长200ms是什么意思？

> 答：可以理解为上传的间隔为200ms，建议音频流每200ms向服务器发送6400字节，发过快可能导致引擎出错，音频发送间隔超时时间为15s，超时服务端报错并主动断开连接。

#### 实时语音转写支不支持离线？

> 答：这个问题有点矛盾；我们有离线识别的api，请使用离线asr api完成请求服务。

#### 实时语音转写如果一次连接使用时长超出了剩余时长怎么办？

> 答：首先为了使业务使用不受影响，如果在连接期间使用时长超出，转写功能并不会立刻停止。本次连接断开后时长可能会出现为负数的情况，请在使用过程中关注时长剩余情况并及时购买时长。
