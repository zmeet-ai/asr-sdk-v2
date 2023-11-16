#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import asyncio
import sys
import json
import time
import argparse
from progress.bar import Bar
import hashlib
import hmac
import time
import base64
from loguru import logger

API_URL = "https://asr-dev.abcpen.com"


def get_signature_flytek(ts, app_id, app_secret):
    tt = (app_id + ts).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(tt)
    baseString = md5.hexdigest()
    baseString = bytes(baseString, encoding="utf-8")

    apiKey = app_secret.encode("utf-8")
    signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
    signa = base64.b64encode(signa)
    signa = str(signa, "utf-8")
    return signa


# 下面的app_id 和api_key仅供测试使用，生产环境请向商务申请(手机：18605811078, 邮箱：jiaozhu@abcpen.com)
app_id = "test1"
app_secret = "2258ACC4-199B-4DCB-B6F3-C2485C63E85A"


async def asr_offline(url_wave, args, audio_encode="mpeg2", audio_sample="16000"):
    timestamp = str(int(time.time()))

    signa = get_signature_flytek(timestamp, app_id, app_secret)
    # signa, timestamp = generate_signature(app_id, app_secret)
    query_post_apply = {
        "ts": timestamp,
        "appid": app_id,
        "signa": signa,
        "sd": "True",
        "input_audio_url": url_wave,
        "audio_encode": audio_encode,
        "audio_sample_rate": audio_sample,
        "has_participle": "false",
    }

    url = f"{API_URL}/v2/asr/long"
    print("\nThe requst para is {}".format(query_post_apply))
    response = requests.post(url, data=query_post_apply)
    print(response.text)

    response_json = json.loads(response.text)
    query_post_task = {"ts": timestamp, "appid": app_id, "signa": signa}
    query_post_task["task_id"] = response_json["data"]["task_id"]

    query_post_result = requests.get(url, query_post_task)
    response_json = json.loads(query_post_result.text)
    bar = Bar("Processing", max=100)
    flag = response_json["code"]
    while flag != "0":
        bar.next()
        await asyncio.sleep(3)
        query_post_result = requests.get(url, query_post_task)
        response_json = json.loads(query_post_result.text)

        flag = response_json["code"]
        if flag == "-1":
            """in progress"""
            bar.next()
            continue

        bflag = int(flag)
        if bflag != 0 and bflag != 1:
            print(
                "\r\nother error-code: {}, desc: {}".format(
                    response_json["code"], response_json["desc"]
                )
            )
            return {"url": url_wave, "asr": response_json["desc"]}
    else:
        response_json = json.loads(query_post_result.text)

        return {"url": url_wave, "asr": response_json}

async def main():
    try:
        parser = argparse.ArgumentParser(
            description="ASR Server offline audio file demo",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "-u",
            "--url",
            type=str,
            metavar="URL",
            help="server url",
            default=f"asr-dev.abcpen.com",
        )
        args = parser.parse_args()

        if len(app_id) <= 0 or len(app_secret) <= 0:
            print("Please apply appid and appsecret, demo will exit now")
            sys.exit(1)
        results = await asyncio.gather(
            asr_offline(
                "https://zmeet-1258547067.cos.ap-shanghai.myqcloud.com/test/amazon_ceo.wav",
                args,
                audio_sample="48000",
            ),
            asr_offline(
                "https://zos.abcpen.com/tts/zmeet/20221023/b6a2c7ac-52c8-11ed-961e-00155dc6cbed.mp3",
                args,
                audio_sample="48000",
            ),
        )
        # results = await asyncio.gather(
        #                        asr_offline("https://zos.abcpen.com/tts/zmeet/20221023/b6a2c7ac-52c8-11ed-961e-00155dc6cbed.mp3", args, audio_sample="48000"))

        print("\n\nWill output the final result in order!")
        for result in results:
            if result:
                print(
                    "Result for {} is ---------------------> {}".format(
                        result["url"], result["asr"]
                    )
                )
                task_id = result["asr"]["data"]["task_id"]
                print(f"task_id is : {task_id}")
            # sd_requst(task_id, 3, 3)
            print("\n\n\n")

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        print("长语音离线识别演示, 演示异步提交请求服务时，返回识别结果依然有序; 该demo返回异步数组请求的json key value pair！")
        asyncio.run(main())
    except KeyboardInterrupt as err:
        logger.error(f"keyboard excpetion: {err}")
    except Exception as e:
        logger.error(f"Got ctrl+c exception-2: {repr(e)}, exit process")

"""
{'code': '0', 'data': {'data': {'speechResult': {'onebest': '除常规的宠物食品，宠物用具外，宠物殡葬，宠物医疗，宠物保险，宠物服务，线下门店等在外界看来颇为小众的领域，
也陆续拿到动辄上千万甚至过亿的投资。近两年，我国一人户家庭数超1.25亿，占比超25%。 2021年，我国饲养猫狗的人群超6800万，其中有近一半 是90后宠物主。当传统家庭结构发生变化，
越来越多年轻人把情感倾注到宠物身上，宠物从单纯的陪伴者晋升为亲密家人，而这些毛孩子们也像人类幼崽一样，有着吃喝拉撒睡，医疗，托管，保险等各种需求，愿意为之付费的宠物主们就
这样浇灌出一个千亿消费市场。', 
'duration': 53928, 'detail': [{'sentences': '除常规的宠物食品，', 'wordBg': '320', 'wordEd': '2320', 'speakerId': '1'}, 
{'sentences': '宠物用具外，', 'wordBg': '2320', 'wordEd': '3720', 'speakerId': '1'}, 
{'sentences': '宠物殡葬，', 'wordBg': '3720', 'wordEd': '4840', 'speakerId': '1'}, 
{'sentences': '宠物医疗，', 'wordBg': '4840', 'wordEd': '6080', 'speakerId': '1'}, 
{'sentences': ' 宠物保险，', 'wordBg': '6080', 'wordEd': '7280', 'speakerId': '1'}, 
{'sentences': '宠物服务，', 'wordBg': '7280', 'wordEd': '8000', 'speakerId': '1'}, 
{'sentences': '线下门店等在外界看来颇为小众的领域，', 'wordBg': '8000', 'wordEd': '11750', 'speakerId': '1'}, 
{'sentences': '也陆续拿到动辄上千万甚至过亿的投资。', 'wordBg': '11750', 'wordEd': '14930', 'speakerId': '0'}, 
{'sentences': '近两年，', 'wordBg': '15420', 'wordEd': '16460', 'speakerId': '0'}, 
{'sentences': '我国一人户家庭数超1.25亿，', 'wordBg': '16460', 'wordEd': '20340', 'speakerId': '0'}, 
{'sentences': '占比超25%。', 'wordBg': '20340', 'wordEd': '22300', 'speakerId': '0'}, 
{'sentences': '2021年，', 'wordBg': '22300', 'wordEd': '23060', 'speakerId': '0'}, 
{'sentences': '我国饲养猫狗的人群超6800万，', 'wordBg': '23060', 'wordEd': '26740', 'speakerId': '0'}, 
{'sentences': '其中有近一半是90后宠物主。', 'wordBg': '26740', 'wordEd': '29200', 'speakerId': '0'}, 
{'sentences': '当传统家庭结构发生变化，', 'wordBg': '29700', 'wordEd': '32300', 'speakerId': '0'}, 
{'sentences': '越来越多年轻人把情感倾注到宠物身上，', 'wordBg': '32300', 'wordEd': '36100', 'speakerId': '0'}, 
{'sentences': '宠物从单纯的陪伴者晋升为亲密家人，', 'wordBg': '36100', 'wordEd': '39780', 'speakerId': '0'}, 
{'sentences': '而这些毛孩子们也像人类幼崽一样，', 'wordBg': '39780', 'wordEd': '42640', 'speakerId': '0'}, 
{'sentences': '有着吃喝拉撒睡，', 'wordBg': '43070', 'wordEd': '44870', 'speakerId': '0'}, 
{'sentences': '医疗，', 'wordBg': '44870', 'wordEd': '45790', 'speakerId': '0'}, 
{'sentences': '托管，', 'wordBg': '45790', 'wordEd': '46510', 'speakerId': '1'}, 
{'sentences': '保险等各种需求，', 'wordBg': '46510', 'wordEd': '48270', 'speakerId': '1'}, 
{'sentences': '愿意为之付费的宠物主们就这样浇灌出一个千亿消费市场。', 'wordBg': '48270', 'wordEd': '53010', 'speakerId': '0'}]}}, 
'task_id': 'cbaf7296-9390-42ae-9163-b986e53bd32e', 'spk_id_text': '', 'audio_denoise_url': '', 
'status': {'spk_id_status': 0, 'denoise_status': 0, 'asr_spk_status': 0}}, 'msg': 'success'}
"""
"""
{'code': '0', 'data': {'data': {'speechResult': {'onebest': '中国共产党第20届中央委员会第一次全体会议，于2012年10月23日在北京举行。
出席全会的有中央委员203人，候补中央委员168人。中央纪律检查委员会委员列席会议。习近平同志主持会议，并在当选中共中央委员会总书记后作了重要讲话。
全会选举了中央政治局委员 ，中央政治局常务委员会委员，中央委员会总书记。根据中央政治局常务委员会的提名，通过了中央书记处成员，决定了中央军事委员会组成人员，
批准了20届中央纪律检查委员会第一次全体会议选举产生的书记，副书记和常务委员会委 员人选名单如下，一中央政治局委员按姓氏笔画为序排列，
丁薛祥，习近平，马兴瑞，王毅，王沪宁，尹力，石泰峰，刘国忠，李希，李强，李干杰，李淑蕾，李鸿忠，何卫东，何立峰，张佑霞，张国清，陈文清，陈吉宁，
陈敏尔，赵乐 际，袁家军，黄坤明，蔡奇。二，中央政治局常务委员会委员，习近平，李强，赵乐际，王沪宁，蔡奇丁薛祥，李希三中央委员会总书记，
习近平四，中央书记处书记蔡奇，石泰峰，李干杰，李书磊，陈文清，刘金国，王晓红五，中央军 事委员会主席，副主席，委员，主席习近平，
副主席张佑霞和卫东为元，李尚福，刘振立，苗华，张生民。六，中央纪律检查委员会书记，副书记，常务委员会委员，书记李希，副书记刘金国，
张生民，肖培，玉红秋女，傅奎，孙新阳， 刘学新，张福海。常务委员会委员按姓氏笔画为序排列，王小平女，王爱文，王洪军，刘金国，刘学新，许罗德，
孙新阳，李希，李欣然满族，肖培，张升民，张福海，陈国强，赵世勇，侯凯银博纳西族，玉红秋女，傅奎穆红玉女。', 'duration': 155736, 
'detail': [{'sentences': '中国共产党第20届中央委员会第一次全体会议，', 'wordBg': '320', 'wordEd': '4400', 'speakerId': '0'}, {'sentences': '于2012年10月23日在北京举行。', 'wordBg': '4400', 'wordEd': '7300', 'speakerId': '1'}, {'sentences': '出席全会的有中央委员203人，', 'wordBg': '8100', 'wordEd': '11260', 'speakerId': '0'}, {'sentences': '候补中央委员168人。', 'wordBg': '11260', 'wordEd': '14060', 'speakerId': '0'}, {'sentences': '中央纪律检查委员会委员列席会议。', 'wordBg': '14060', 'wordEd': '16720', 'speakerId': '0'}, {'sentences': '习近平同志主持会议，', 'wordBg': '17460', 'wordEd': '19300', 'speakerId': '0'}, {'sentences': '并在当选中共中央委员会总书记后作了重要讲话。', 'wordBg': '19300', 'wordEd': '23040', 'speakerId': '0'}, {'sentences': '全会选举了中央政治局委员，', 'wordBg': '23820', 'wordEd': '26260', 'speakerId': '0'}, {'sentences': '中央政治局常务委员会委员，', 'wordBg': '26260', 'wordEd': '28580', 'speakerId': '0'}, {'sentences': '中央委员会总书记。', 'wordBg': '28580', 'wordEd': '30380', 'speakerId': '0'}, {'sentences': '根据中央政治局常务委员会的提名，', 'wordBg': '30380', 'wordEd': '33220', 'speakerId': '0'}, {'sentences': '通过了中央书记处成员，', 'wordBg': '33220', 'wordEd': '35220', 'speakerId': '0'}, {'sentences': '决定了中央军事委员会组成人员，', 'wordBg': '35220', 'wordEd': '37520', 'speakerId': '0'}, {'sentences': '批准了20届中央纪律检查委员会第一次全体会议选举产生的书记，', 'wordBg': '38020', 'wordEd': '43700', 'speakerId': '0'}, {'sentences': '副书记和常务委员会委员人选名单如下，', 'wordBg': '43700', 'wordEd': '48500', 'speakerId': '0'}, {'sentences': '一中央政治局委员按姓氏笔画为序排列，', 'wordBg': '48500', 'wordEd': '53040', 'speakerId': '1'}, {'sentences': '丁薛祥，', 'wordBg': '53740', 'wordEd': '54700', 'speakerId': '1'}, {'sentences': '习近平，', 'wordBg': '54700', 'wordEd': '55540', 'speakerId': '1'}, {'sentences': '马兴瑞，', 'wordBg': '55540', 'wordEd': '56420', 'speakerId': '1'}, {'sentences': '王毅，', 'wordBg': '56420', 'wordEd': '57100', 'speakerId': '1'}, {'sentences': '王沪宁，', 'wordBg': '57100', 'wordEd': '57980', 'speakerId': '1'}, {'sentences': '尹力，', 'wordBg': '57980', 'wordEd': '58740', 'speakerId': '1'}, {'sentences': '石泰峰，', 'wordBg': '58740', 'wordEd': '59620', 'speakerId': '1'}, {'sentences': '刘国忠，', 'wordBg': '59620', 'wordEd': '60420', 'speakerId': '1'}, {'sentences': '李希，', 'wordBg': '60420', 'wordEd': '61100', 'speakerId': '1'}, {'sentences': '李强，', 'wordBg': '61100', 'wordEd': '61820', 'speakerId': '1'}, {'sentences': '李干杰，', 'wordBg': '61820', 'wordEd': '62660', 'speakerId': '1'}, {'sentences': '李淑蕾，', 'wordBg': '62660', 'wordEd': '63540', 'speakerId': '1'}, {'sentences': '李鸿忠，', 'wordBg': '63540', 'wordEd': '64380', 'speakerId': '1'}, {'sentences': '何卫东，', 'wordBg': '64380', 'wordEd': '65220', 'speakerId': '1'}, {'sentences': '何立峰，', 'wordBg': '65220', 'wordEd': '66020', 'speakerId': '1'}, {'sentences': '张佑霞，', 'wordBg': '66020', 'wordEd': '66940', 'speakerId': '1'}, {'sentences': '张国清，', 'wordBg': '66940', 'wordEd': '67440', 'speakerId': '1'}, {'sentences': '陈文清，', 'wordBg': '67840', 'wordEd': '68760', 'speakerId': '1'}, {'sentences': '陈吉宁，', 'wordBg': '68760', 'wordEd': '69680', 'speakerId': '1'}, {'sentences': '陈敏尔，', 'wordBg': '69680', 'wordEd': '70520', 'speakerId': '1'}, {'sentences': '赵乐际，', 'wordBg': '70520', 'wordEd': '71400', 'speakerId': '1'}, {'sentences': '袁家军，', 'wordBg': '71400', 'wordEd': '72400', 'speakerId': '1'}, {'sentences': ' 黄坤明，', 'wordBg': '72400', 'wordEd': '73360', 'speakerId': '1'}, {'sentences': '蔡奇。', 'wordBg': '73360', 'wordEd': '74480', 'speakerId': '1'}, {'sentences': '二，', 'wordBg': '74480', 'wordEd': '75200', 'speakerId': '0'}, {'sentences': '中央政治局常务委员会委员，', 'wordBg': '75200', 'wordEd': '77220', 'speakerId': '0'}, {'sentences': '习近平，', 'wordBg': '78040', 'wordEd': '78960', 'speakerId': '1'}, {'sentences': '李强，', 'wordBg': '78960', 'wordEd': '79720', 'speakerId': '1'}, {'sentences': '赵乐际，', 'wordBg': '79720', 'wordEd': '80560', 'speakerId': '1'}, {'sentences': '王沪宁，', 'wordBg': '80560', 'wordEd': '81560', 'speakerId': '1'}, {'sentences': '蔡奇丁薛祥，', 'wordBg': '81560', 'wordEd': '83160', 'speakerId': '1'}, {'sentences': '李希三中央委员会总书记，', 'wordBg': '83160', 'wordEd': '87340', 'speakerId': '0'}, {'sentences': '习近平四，', 'wordBg': '87340', 'wordEd': '89500', 'speakerId': '1'}, {'sentences': '中央书记处书记蔡奇，', 'wordBg': '89500', 'wordEd': '92400', 'speakerId': '0'}, {'sentences': '石泰 峰，', 'wordBg': '92400', 'wordEd': '93280', 'speakerId': '1'}, {'sentences': '李干杰，', 'wordBg': '93280', 'wordEd': '94280', 'speakerId': '1'}, {'sentences': '李书磊，', 'wordBg': '94280', 'wordEd': '95280', 'speakerId': '0'}, {'sentences': '陈文清，', 'wordBg': '95280', 'wordEd': '96240', 'speakerId': '1'}, {'sentences': '刘金国，', 'wordBg': '96240', 'wordEd': '97200', 'speakerId': '1'}, {'sentences': '王晓红 五，', 'wordBg': '97200', 'wordEd': '99240', 'speakerId': '0'}, {'sentences': '中央军事委员会主席，', 'wordBg': '99240', 'wordEd': '101240', 'speakerId': '0'}, {'sentences': '副主席，', 'wordBg': '101240', 'wordEd': '102120', 'speakerId': '1'}, {'sentences': '委员，', 'wordBg': '102120', 'wordEd': '102420', 'speakerId': '0'}, {'sentences': '主席习近平，', 'wordBg': '103280', 'wordEd': '105800', 'speakerId': '1'}, {'sentences': '副主席张佑霞和卫东为元，', 'wordBg': '105800', 'wordEd': '110320', 'speakerId': '1'}, {'sentences': '李尚福，', 'wordBg': '110320', 'wordEd': '111280', 'speakerId': '1'}, {'sentences': '刘振立，', 'wordBg': '111280', 'wordEd': '112240', 'speakerId': '1'}, {'sentences': '苗华，', 'wordBg': '112240', 'wordEd': '112960', 'speakerId': '1'}, {'sentences': '张生民。', 'wordBg': '112960', 'wordEd': '113460', 'speakerId': '1'}, {'sentences': '六，', 'wordBg': '114280', 'wordEd': '114960', 'speakerId': '0'}, {'sentences': '中央纪律检查委员会书记，', 'wordBg': '114960', 'wordEd': '117400', 'speakerId': '0'}, {'sentences': '副书记，', 'wordBg': '117400', 'wordEd': '118320', 'speakerId': '1'}, {'sentences': '常务委员会委员，', 'wordBg': '118320', 'wordEd': '119460', 'speakerId': '0'}, {'sentences': '书记李希，', 'wordBg': '120380', 'wordEd': '122740', 'speakerId': '1'}, {'sentences': '副书记刘金国，', 'wordBg': '122740', 'wordEd': '124580', 'speakerId': '1'}, {'sentences': '张生民，', 'wordBg': '124580', 'wordEd': '125500', 'speakerId': '1'}, {'sentences': '肖培，', 'wordBg': '125500', 'wordEd': '126300', 'speakerId': '1'}, {'sentences': '玉红秋女，', 'wordBg': '126300', 'wordEd': '127780', 'speakerId': '1'}, {'sentences': '傅奎，', 'wordBg': '127780', 'wordEd': '128580', 'speakerId': '1'}, {'sentences': '孙新阳，', 'wordBg': '128580', 'wordEd': '129540', 'speakerId': '1'}, {'sentences': '刘学新，', 'wordBg': '129540', 'wordEd': '130380', 'speakerId': '1'}, {'sentences': '张福海。', 'wordBg': '130380', 'wordEd': '130880', 'speakerId': '0'}, {'sentences': '常务委员会委员按姓氏笔画为序排列，', 'wordBg': '131700', 'wordEd': '135080', 'speakerId': '1'}, {'sentences': '王小平女，', 'wordBg': '135800', 'wordEd': '137280', 'speakerId': '1'}, {'sentences': '王爱文，', 'wordBg': '137280', 'wordEd': '138160', 'speakerId': '0'}, {'sentences': '王洪军，', 'wordBg': '138160', 'wordEd': '139000', 'speakerId': '1'}, {'sentences': '刘金国，', 'wordBg': '139000', 'wordEd': '139880', 'speakerId': '1'}, {'sentences': '刘学新，', 'wordBg': '139880', 'wordEd': '140760', 'speakerId': '1'}, {'sentences': '许罗德，', 'wordBg': '140760', 'wordEd': '141600', 'speakerId': '1'}, {'sentences': '孙新阳，', 'wordBg': '141600', 'wordEd': '142520', 'speakerId': '1'}, {'sentences': '李希，', 'wordBg': '142520', 'wordEd': '143160', 'speakerId': '1'}, {'sentences': '李欣然满族，', 'wordBg': '143160', 'wordEd': '144760', 'speakerId': '1'}, {'sentences': '肖培，', 'wordBg': '144760', 'wordEd': '145560', 'speakerId': '1'}, {'sentences': '张升民，', 'wordBg': '145560', 'wordEd': '146440', 'speakerId': '1'}, {'sentences': '张福海，', 'wordBg': '146440', 'wordEd': '147400', 'speakerId': '1'}, {'sentences': '陈国强，', 'wordBg': '147400', 'wordEd': '148360', 'speakerId': '1'}, {'sentences': '赵世勇，', 'wordBg': '148360', 'wordEd': '149200', 'speakerId': '0'}, {'sentences': '侯凯银博纳西族，', 'wordBg': '149200', 'wordEd': '151600', 'speakerId': '1'}, {'sentences': '玉红秋女，', 'wordBg': '151600', 'wordEd': '153080', 'speakerId': '1'}, {'sentences': '傅奎穆红玉女。', 'wordBg': '153080', 'wordEd': '154820', 'speakerId': '1'}]}}, 'task_id': 'e219e532-5836-48b5-8ccb-d01711f6ba55', 'spk_id_text': '', 'audio_denoise_url': '', 'status': {'spk_id_status': 0, 'denoise_status': 0, 'asr_spk_status': 0}}, 'msg': 'success'}
"""
