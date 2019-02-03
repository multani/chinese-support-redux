# Copyright 2012 Roland Sieker <ospalh@gmail.com>
# Copyright 2012 Thomas TEMPÉ <thomas.tempe@alysse.org>
# Copyright 2017 Pu Anlai
# Copyright 2017-2018 Joseph Lorimer <luoliyan@posteo.net>
# Inspiration: Tymon Warecki
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html

from os.path import basename, exists, join
from re import sub
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import requests
from aqt import mw
from gtts import gTTS


requests.packages.urllib3.disable_warnings()


def download_sound(text, source=('google', 'zh-cn')):
    service, lang = source

    if service == 'google':
        path = get_path(text, source)
    elif service == 'baidu':
        path = get_path(text, source)
    elif service == 'aws':
        path = get_path(text, source)

    if exists(path):
        return basename(path)

    if service == 'google':
        # should raise ValueError on unsupported lang code
        tts = gTTS(text, lang=lang)
        tts.save(path)
    elif service == 'baidu':
        download_baidu(text, lang, path)
    elif service == 'aws':
        download_aws(text, lang, path)

    return basename(path)


def get_path(text, source):
    service, lang = source
    filename = '{}_{}_{}.mp3'.format(sanitize(text), service, lang)
    return join(mw.col.media.dir(), filename)


def sanitize(s):
    return sub(r'[\/:\*?"<>\|]', '', s)


def download_baidu(text, lang, path):
    # http://tts.baidu.com/text2audio?lan=zh&ie=UTF-8&text={text}
    def buildUrl(text, lang):
        url_gtts = 'http://tts.baidu.com/text2audio?'
        query = dict(lan=lang, ie='UTF-8', text=text.encode('utf-8'))
        return url_gtts + urlencode(query)

    request = Request(buildUrl(text, lang))
    request.add_header('User-Agent', 'Mozilla/5.0')
    response = urlopen(request, timeout=5)

    if response.code != 200:
        raise ValueError(str(response.code) + ': ' + response.msg)
    with open(path, 'wb') as audio:
        audio.write(response.read())

def download_aws(value, lang, path):
    kw = {
        "region_name": "eu-west-3",
        "profile_name": "myown",
        # "aws_access_key_id": aws.get("access_key"),
        # "aws_secret_access_key": aws.get("secret_key"),
    }

    import boto3
    session = boto3.Session(**kw)
    polly = session.client("polly")

    polly_voice = "Zhiyu"
    output_format = "mp3"

    print("Synthesizing: Voice={}, Format={}, Text={}".format(
        polly_voice, output_format, value
    ))
    response = polly.synthesize_speech(
        VoiceId=polly_voice,
        OutputFormat=output_format,
        Text=value,
    )

    with open(path, "wb") as fp:
        fp.write(response["AudioStream"].read())
