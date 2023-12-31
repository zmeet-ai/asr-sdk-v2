## 录音文件识别请求

### 1. 接口描述

接口请求域名： https://asr-prod.abcpen.com/v2/asr/long

- 本接口可对较长的录音文件进行识别。
- 接口默认限频：20次/秒。此处仅限制任务提交频次，与识别结果返回时效无关
- 返回时效：异步回调，非实时返回。最长3小时返回识别结果，**大多数情况下，1小时的音频1-3分钟即可完成识别**。请注意：上述返回时长不含音频下载时延，且30分钟内发送超过1000小时录音或2万条任务的情况除外
- 媒体文件格式：**支持几乎所有音视频文件格式**，如mp4, avi, mkv, mov, wmv, flv, webm, mpeg, mpg, h264, hevc, wav、mp3、m4a、flv、mp4、wma、3gp、amr、aac、ogg-opus、flac
- 支持语言：[支持100种国家语言](https://github.com/zmeet-ai/asr-sdk-v2/blob/main/docs/country_code.md)
-  音频提交方式：本接口支持**音频 URL 、本地音频文件**两种请求方式。推荐使用[阿里云对象存储OSS](https://www.aliyun.com/product/oss?spm=5176.28508143.J_4VYgf18xNlTAyFFbOuOQe.60.e939154aMOdAFn) 、[亚马逊S3](about:blank)和 [腾讯云COS](https://cloud.tencent.com/document/product/436/38484) 等对象存储来存储、生成URL并提交任务，存储桶权限需要设置公有读私有写，或URL设置外部可访问
-  音频限制：音频 URL 时长不能大于5小时，文件大小不超过1GB；本地音频文件不能大于5MB
-  如何获取识别结果：支持**回调或轮询**的方式获取结果，具体请参考 [录音文件识别结果查询](https://cloud.tencent.com/document/product/1093/37822)
-  识别结果有效时间：在服务端保存7天
-  签名方法参考 [公共参数](https://github.com/zmeet-ai/asr-sdk-v2/blob/main/docs/signature.md) 中签名方法

默认接口请求频率限制：20次/秒。



### 2. 输入参数

以下请求参数列表仅列出了接口请求参数，完整公共参数列表见 [公共请求参数](https://github.com/zmeet-ai/asr-sdk-v2/blob/main/docs/signature.md)。

| 参数名称           | 必选 | 类型    | 描述                                                         | 默认值 |
| :----------------- | :--- | :------ | :----------------------------------------------------------- | ------ |
| scene              | 否   | String  | 法院: court <br/>教育: edu <br/>金融: finance <br/>医疗: medical <br/>科技: tech <br/>运营商: isp <br/>政府: gov <br/>电商: ecom <br/>军事: mil <br/>企业: com <br/>生活: life <br/>汽车: car<br/> |        |
| is_tel             | 否   | Integer | 1.  电话通讯场景引擎： **注意：电话通讯场景下，请务必设置该字段位1。如您有电话通讯场景识别需求，但没有设置该字段，亦能获取识别结果**， 但因为细分场景并非基于电话通讯数据训练，无法承诺此种调用方式的识别效果，需由您自行验证识别结果是否可用。<br/>2. 电话通讯场景录制的音频，一般是8K双声道，双声道能够物理区分说话人、避免说话双方重叠产生的识别错误，能达到最好的说话人分离效果和识别效果。设置双声道后，将自动区分说话人，因此**无需再开启说话人分离功能**，相关参数（**SpeakerDiarization、SpeakerNumber**） |        |
| ChannelNum         | 是   | Integer | 识别声道数 1：单声道（16k音频仅支持单声道，**请勿**设置为双声道）； 2：双声道（仅支持8k电话音频，且双声道应分别为通话双方）  注意： • 16k音频：仅支持单声道识别，**需设置ChannelNum=1**； • 8k电话音频：支持单声道、双声道识别，**建议设置ChannelNum=2，即双声道**。使用默认值即可 示例值：1 |        |
| ResTextFormat      | 是   | Integer | 识别结果返回样式 0：基础识别结果（仅包含有效人声时间戳，无词粒度的[详细识别结果](https://cloud.tencent.com/document/api/1093/37824#SentenceDetail)）； 1：基础识别结果之上，增加词粒度的[详细识别结果](https://cloud.tencent.com/document/api/1093/37824#SentenceDetail)（包含词级别时间戳、语速值，**不含标点**）； 2：基础识别结果之上，增加词粒度的[详细识别结果](https://cloud.tencent.com/document/api/1093/37824#SentenceDetail)（包含词级别时间戳、语速值和标点）； 3：基础识别结果之上，增加词粒度的[详细识别结果](https://cloud.tencent.com/document/api/1093/37824#SentenceDetail)（包含词级别时间戳、语速值和标点），且识别结果按标点符号分段，**适用字幕场景**； 4：**【增值付费功能】**基础识别结果之上，增加词粒度的[详细识别结果](https://cloud.tencent.com/document/api/1093/37824#SentenceDetail)（包含词级别时间戳、语速值和标点），且识别结果按nlp语义分段，**适用会议、庭审记录转写等场景**，仅支持8k_zh/16k_zh引擎 5：**【增值付费功能】**基础识别结果之上，增加词粒度的[详细识别结果](https://cloud.tencent.com/document/api/1093/37824#SentenceDetail)（包含词级别时间戳、语速值和标点），并输出口语转书面语转写结果，该结果去除语气词、重复词、精简冗余表达，并修正发言人口误，实现口语转书面语的效果，**适用于线上、线下会议直接总结为书面会议纪要的场景**，仅支持8k_zh/16k_zh引擎  注意： 如果传入参数值4，需确保账号已购买[语义分段资源包](https://cloud.tencent.com/document/product/1093/35686#97ae4aa0-29a0-4066-9f07-ccaf8856a16b)，或账号开启后付费；**若当前账号已开启后付费功能，并传入参数值4，将[自动计费](https://cloud.tencent.com/document/product/1093/35686#d912167d-ffd5-41a9-8b1c-2e89845a6852)** 如果传入参数值5，需确保账号已购买[口语转书面语资源包](https://cloud.tencent.com/document/product/1093/35686#97ae4aa0-29a0-4066-9f07-ccaf8856a16b)，或账号开启后付费；**若当前账号已开启后付费功能，并传入参数值5，将自动计费[自动计费](https://cloud.tencent.com/document/product/1093/35686#d912167d-ffd5-41a9-8b1c-2e89845a6852)** 示例值：0 |        |
| SourceType         | 是   | Integer | 音频数据来源 0：音频URL； 1：音频数据（post body） 示例值：0 |        |
| Data               | 否   | String  | 音频数据base64编码 **当 SourceType 值为 1 时须填写该字段，为 0 时不需要填写**  注意：音频数据要小于5MB（含） |        |
| DataLen            | 否   | Integer | 数据长度（此数据长度为数据未进行base64编码时的长度）         |        |
| Url                | 否   | String  | 音频URL的地址（需要公网环境浏览器可下载） **当 SourceType 值为 0 时须填写该字段，为 1 时不需要填写**  注意： 1. 请确保录音文件时长在5个小时（含）之内，否则可能识别失败； 2. 请保证文件的下载速度，否则可能下载失败 示例值：https://audio.cos.ap-guangzhou.myqcloud.com/example.wav |        |
| CallbackUrl        | 否   | String  | 回调 URL 用户自行搭建的用于接收识别结果的服务URL 回调格式和内容详见：[录音识别回调说明](https://cloud.tencent.com/document/product/1093/52632)  注意： 如果用户使用轮询方式获取识别结果，则无需提交该参数 |        |
| SpeakerDiarization | 否   | Integer | 是否开启说话人分离 0：不开启； 1：开启（仅支持以下引擎：8k_zh/16k_zh/16k_ms/16k_en/16k_id，且ChannelNum=1时可用）； 默认值为 0  注意： 8k双声道电话音频请按 **ChannelNum 识别声道数** 的参数描述使用默认值 示例值：0 |        |
| SpeakerNumber      | 否   | Integer | 说话人分离人数 **需配合开启说话人分离使用，不开启无效**，取值范围：0-10 0：自动分离（最多分离出20个人）； 1-10：指定人数分离； 默认值为 0 示例值：0 |        |
| HotwordId          | 否   | String  | 热词表id 如不设置该参数，将自动生效默认热词表； 如设置该参数，将生效对应id的热词表； 点击这里查看[热词表配置方法](https://cloud.tencent.com/document/product/1093/40996) |        |
| ReinforceHotword   | 否   | Integer | 热词增强功能（目前仅支持8k_zh/16k_zh引擎） 1：开启热词增强功能  注意：热词增强功能开启后，将对传入的热词表id开启同音替换功能，可以在这里查看[热词表配置方法](https://cloud.tencent.com/document/product/1093/40996)。效果举例：在热词表中配置“蜜制”一词，并开启增强功能，与“蜜制”（mìzhì）同音同调的“秘制”（mìzhì）的识别结果会被强制替换成“蜜制”。**建议客户根据实际的业务需求开启该功能** 示例值：0 |        |
| CustomizationId    | 否   | String  | 自学习定制模型 id 如设置了该参数，将生效对应id的自学习定制模型； 点击这里查看[自学习定制模型配置方法](https://cloud.tencent.com/document/product/1093/38416) |        |
| EmotionRecognition | 否   | Integer | **【增值付费功能】**情绪识别能力（目前仅支持16k_zh,8k_zh） 0：不开启； 1：开启情绪识别，但不在文本展示情绪标签； 2：开启情绪识别，并且在文本展示情绪标签（**该功能需要设置ResTextFormat 大于0**） 默认值为0 支持的情绪分类为：高兴、伤心、愤怒  注意： 1. **本功能为增值服务**，需将参数设置为1或2时方可按对应方式生效； 2. 如果传入参数值1或2，需确保账号已购买[情绪识别资源包](https://cloud.tencent.com/document/product/1093/35686#97ae4aa0-29a0-4066-9f07-ccaf8856a16b)，或账号开启后付费；**若当前账号已开启后付费功能，并传入参数值1或2，将[自动计费](https://cloud.tencent.com/document/product/1093/35686#d912167d-ffd5-41a9-8b1c-2e89845a6852)）**； 3. 参数设置为0时，无需购买资源包，也不会消耗情绪识别对应资源 示例值：0 |        |
| EmotionalEnergy    | 否   | Integer | 情绪能量值 取值为音量分贝值/10，取值范围：[1,10]，值越高情绪越强烈 0：不开启； 1：开启； 默认值为0 示例值：0 |        |
| ConvertNumMode     | 否   | Integer | 阿拉伯数字智能转换（目前仅支持8k_zh/16k_zh引擎） 0：不转换，直接输出中文数字； 1：根据场景智能转换为阿拉伯数字； 3：打开数学相关数字转换（如：阿尔法转写为α）； 默认值为 1 示例值：0 |        |
| FilterDirty        | 否   | Integer | 脏词过滤（目前仅支持8k_zh/16k_zh引擎） 0：不过滤脏词； 1：过滤脏词； 2：将脏词替换为 * ； 默认值为 0 示例值：0 |        |
| FilterPunc         | 否   | Integer | 标点符号过滤（目前仅支持8k_zh/16k_zh引擎） 0：不过滤标点； 1：过滤句末标点； 2：过滤所有标点； 默认值为 0 示例值：0 |        |
| FilterModal        | 否   | Integer | 语气词过滤（目前仅支持8k_zh/16k_zh引擎） 0：不过滤语气词； 1：过滤部分语气词； 2：严格过滤语气词； 默认值为 0 示例值：0 |        |
| SentenceMaxLength  | 否   | Integer | 单标点最多字数 **可控制单行字幕最大字数，适用于字幕生成场景**，取值范围：[6，40] 0：不开启该功能； 默认值为0  注意：需设置ResTextFormat为3，解析返回的ResultDetail列表，通过结构中FinalSentence获取单个标点断句结果 示例值：0 |        |
| Extra              | 否   | String  | 附加参数**（该参数无意义，忽略即可）**                       |        |

### 3. 输出参数

| 参数名称  | 类型                                                         | 描述                                                         |
| :-------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| Data      | [Task](https://cloud.tencent.com/document/api/1093/37824#Task) | 录音文件识别的请求返回结果，包含结果查询需要的TaskId         |
| RequestId | String                                                       | 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。 |

### 4. 示例

### 示例1 通过音频Url来调用接口

用户通过音频Url的方式（SourceType为0）请求录音识别服务，请求模型为16k中文 （EngineModelType = 16k_zh），音频格式为wav（采样率为16k，单声道）

#### 输入示例