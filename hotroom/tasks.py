#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-02-16 15:17:47
# @Author  : eclipse_sv (eclipse_sv@163.com)
# @Link    : https://eclipsesv.com
# @Version : $Id$
from celeryApp import app
from collector.danmu.douyu import parase_douyu_room_info, douyu_all_rooms
from collector.danmu.panda import get_panda_room_urls, save_panda_room_info
from collector.danmu.quanmin import generate_qm_room_urls, save_qm_roominfo


@app.task(max_retries=3, default_retry_delay=1 * 6)
def SAVE_PANDA_ROOM_DELAY(url):
    save_panda_room_info(url)


@app.task(max_retries=3, default_retry_delay=1 * 6)
def SAVE_DOUYU_ROOM_DELAY(url):
    parase_douyu_room_info(url)


@app.task
def SAVE_DOUYU_INFO():
    for item in douyu_all_rooms():
        SAVE_DOUYU_ROOM_DELAY.delay(item)


@app.task
def SAVE_PANDA_INFO():
    for item in get_panda_room_urls():
        SAVE_PANDA_ROOM_DELAY.delay(item)


@app.task
def SAVE_QUANMIN_INFO():
    for url in generate_qm_room_urls():
        SAVE_QUANMIN_ROOM_DELAY.delay(url)


@app.task(max_retries=3, default_retry_delay=1 * 6)
def SAVE_QUANMIN_ROOM_DELAY(url):
    save_qm_roominfo(url)
