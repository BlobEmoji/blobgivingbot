# -*- coding: utf-8 -*-

import asyncio
import logging

import uvloop

import config
from blobgivingbot import BlobGivingBot


log = logging.getLogger()
log.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

handler = logging.FileHandler(filename='blobgivingbot.log', encoding='utf-8', mode='a')
handler.setFormatter(formatter)
log.addHandler(handler)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


bot = BlobGivingBot()
bot.run(config.token)
