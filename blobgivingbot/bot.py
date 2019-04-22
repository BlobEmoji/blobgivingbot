# -*- coding: utf-8 -*-

import logging

import discord
from discord.ext import commands

import config


log = logging.getLogger(__name__)


class BlobGivingBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            activity=config.activity,
            command_prefix=config.prefix,
            fetch_offline_members=False,
            owner_id=config.owner_id,
        )

        self.load_extension('jishaku')
        self.load_extension('blobgivingbot.giveaways')

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        if channel_id not in config.command_channels and channel_id != config.giveaway_channel:
            return

        await self.process_commands(message)

    async def on_error(self, event_method, *args, **kwargs):
        log.exception(f'Ran into an error in the {event_method} event.')

    async def on_command_error(self, context, exception):
        log.exception(f'Ran into an error while running the {context.command.name} command.', exc_info=exception)
