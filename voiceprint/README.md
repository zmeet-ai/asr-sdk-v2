# 声纹识别API文档
## 一、注册声纹
### POST /register
注册说话人的声纹信息到系统中, 如果已经 org_id + tag_id +spk_name 的组合已经存在，则返回已经存在同名的提示；否则继续注册。
- 请求参数:

| 参数名 | 类型 | 是否必需 | 描述 | 备注 |
|--------|------|----------|------|--------|
| spk_name | string | 是 | 说话人名称,在org_id和tag_id组合内唯一 | 命名需要是英文字母、数字组合，中间不可以有空格。 |
| org_id | string | 是 | 组织ID | 命名需要是英文字母、数字组合，中间不可以有空格。 |
| tag_id | string | 是 | 标签ID | 命名需要是英文字母、数字组合，中间不可以有空格。 |
| audio | file | 是 | 音频文件 | * 语音文件不要超过5分钟，否则会自动截断出前5分钟；语音文件最短需要0.2秒以上，否则注册失败（强烈建议是2秒或以上的时间）。<br/>* 注册的语音文件要求如下：<br/>    * 需要背景干净没有噪音，同时只有一个人说话。<br/>    * 读取任何一段文本，读取的时候，标点符号中间要做适度的停顿，比如停留1秒左右的时间，尤其是大的标点符号句号”。“，问号“？” |
| app_id | string | 是 | 应用ID(通过认证获取， 具体参考sdk示例代码) |  |
| audio_preprocess | bool | 否 | 语音是否预处理 | 默认为false, 不建议设置为True，除非特殊场景 |
| denoise_enable | bool | 否 | 语音是否自动降噪 | 默认为false，在噪声背景下打开该参数，打开会增加相应的处理时间 |


- 响应:
```json
{
   "code":"0",
   "msg":"success",
   "data":{
      "audio_url":"https://zos.abcpen.com/voiceid/lianxintest2/20250108/178fe352-0383-43aa-8a5c-37eb3c51f1c0.wav"
   }
}
```

## 二、更新声纹
### POST /update
更新已存在说话人的声纹信息。
-  请求参数:


| 参数名 | 类型 | 是否必需 | 描述 | 备注 |
|--------|------|----------|------|------|
| spk_name | string | 是 | 说话人名称 | 命名需要是英文字母、数字组合，中间不可以有空格。 |
| org_id | string | 是 | 组织ID | 命名需要是英文字母、数字组合，中间不可以有空格。 |
| tag_id | string | 是 | 标签ID | 命名需要是英文字母、数字组合，中间不可以有空格。 |
| audio | file | 是 | 新的音频文件 | * 语音文件不要超过5分钟，否则会自动截断出前5分钟；语音文件最短需要0.2秒以上（强烈建议是2秒或以上的时间），否则注册失败。<br/>* 注册的语音文件，需要背景干净没有噪音，同时只有一个人说话。<br/>* 如果识别的语音有超过1个人的语音，我们从中选择**某人语音时长最长的人做识别** |
| app_id | string | 是 | 应用ID(通过认证获取) |  |


- 响应:
```json
{
    "code": "0", 
    "msg": "success",
    "data": {
        "audio_url": "音频文件URL"
    }
}
```

## 三、声纹识别
### POST /recognize
对上传的音频进行声纹识别。
- 请求参数:

| 参数名 | 类型 | 是否必需 | 描述 |
|--------|------|----------|------|
| audio | file | 是 | 待识别的音频文件，注意：<br/>* 语音文件不要超过5分钟，否则会自动截断出前5分钟；语音文件最短需要0.2秒以上（强烈建议是2秒或以上的时间），否则注册失败。<br/>* 注册的语音文件，需要背景干净没有噪音，同时只有一个人说话。<br/>* 如果识别的语音有超过1个人的语音，我们从中选择**某人语音时长最长的人做识别** |
| org_id | string | 是 | 组织ID |
| tag_id | string | 是 | 标签ID |
| app_id | string | 是 | 应用ID(通过认证获取) |

- 响应:
```json
{
   "code":"0",
   "msg":"success",
   "data":[
      {
         "spk_name":"张明",
         "audio_path":"https://zos.abcpen.com/voiceid/lianxintest2/20250108/178fe352-0383-43aa-8a5c-37eb3c51f1c0.wav",
         "score":0.7805231213569641,
         "tag":"lianxintest2"
      }
   ]
}
```
## 四、获取声纹音频URL
### GET /voice-url
- 请求参数:

| 参数名 | 类型 | 是否必需 | 描述 |
|--------|------|----------|------|
| spk_name | string | 是 | 说话人名称 |
| org_id | string | 是 | 组织ID |
| tag_id | string | 是 | 标签ID |
| app_id | string | 是 | 应用ID(通过认证获取) |

- 响应:
```json
{
   "code":"0",
   "msg":"success",
   "data":{
      "audio_path":"https://zos.abcpen.com/voiceid/lianxintest2/20250108/178fe352-0383-43aa-8a5c-37eb3c51f1c0.wav"
   }
}
```
## 五、获取声纹列表
### GET /list
- 请求参数:

| 参数名 | 类型 | 是否必需 | 描述 |
|--------|------|----------|------|
| org_id | string | 是 | 组织ID |
| tag_id | string | 是 | 标签ID |
| offset | integer | 否 | 分页偏移量,默认0 |
| limit | integer | 否 | 每页记录数,默认20 |
| app_id | string | 是 | 应用ID(通过认证获取) |

- 响应:
```json
{
   "code":"0",
   "msg":"success",
   "data":[
      {
         "spk_name":"张明",
         "audio_path":"https://zos.abcpen.com/voiceid/lianxintest2/20250108/178fe352-0383-43aa-8a5c-37eb3c51f1c0.wav"
      }
   ]
}
```
##  六、获取声纹数量
GET /count
- 请求参数:

| 参数名 | 类型 | 是否必需 | 描述 |
|--------|------|----------|------|
| org_id | string | 是 | 组织ID |
| tag_id | string | 是 | 标签ID |
| app_id | string | 是 | 应用ID(通过认证获取) |

- 响应:
```json
 {"code":"0","msg":"success","data":{"count":1}}
```

## 七、删除声纹
GET /delete-speakers

- 请求参数:

| 参数名 | 类型 | 是否必需 | 描述 |
|--------|------|----------|------|
| org_id | string | 是 | 组织ID |
| tag_id | string | 是 | 标签ID |
| speaker | array | 否 | 要删除的说话人列表 |
| app_id | string | 是 | 应用ID(通过认证获取) |

- 响应:

```json
{"code":"0","msg":"success","data":1}
```

## 注意事项:

* 所有接口的参数名称(spk_name、app_id、org_id、tag_id)只能包含字母数字,不能包含特殊字符

* 所有接口都需要通过认证获取app_id

* 错误码说明:
    * 0: 成功
    * 10002: 操作失败
    * 10003: 识别失败
    * 10106: 系统错误
    * 10111: HTTP异常