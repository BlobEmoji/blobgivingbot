# -*- coding: utf-8 -*-

import discord
from discord.ext import commands

import config

from .utils import Timer


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

        if message.channel.id not in config.command_channels:
            return

        await self.process_commands(message)

    @commands.command(aliases=['ping', 'p'])
    async def rtt(self, ctx: commands.Context):
        """Shows the bots HTTP and websocket latency to Discord."""
        with Timer() as rtt:
            msg = await ctx.send('...')

        ws = self.latency * 1000
        await msg.edit(content=f'Pong! rtt: {rtt}, ws: {ws:.3f}ms')
