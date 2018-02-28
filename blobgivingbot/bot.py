# -*- coding: utf-8 -*-

import logging

import discord
from discord.ext import commands

import config

from .utils import Timer


log = logging.getLogger(__name__)


class BlobGivingBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=config.prefix,
            owner_id=config.owner_id,
            fetch_offline_members=False,
        )

        self.add_command(self.rtt)
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

    @commands.command(aliases=['ping', 'p'])
    async def rtt(self, ctx: commands.Context):
        """Shows the bots HTTP and websocket latency to Discord."""
        with Timer() as rtt:
            msg = await ctx.send('...')

        ws = self.latency * 1000
        await msg.edit(content=f'Pong! rtt: {rtt}, ws: {ws:.3f}ms')
