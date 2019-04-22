# -*- coding: utf-8 -*-

import datetime

import discord


token = 'beep.boop.secret'

prefix = '$'
owner_id = 69198249432449024

giveaway_channel = 384121527437885440
giveaway_emoji = 384394753749417996

giveaway_duration = datetime.timedelta(days=1)

# channels in which the bot responds to commands, all others are ignored
command_channels = {384121527437885440}

activity = discord.Game('https://blobs.gg')
