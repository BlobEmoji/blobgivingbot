# -*- coding: utf-8 -*-

import asyncio
import datetime
import logging
import random

import discord
from discord.ext import commands

from .bot import BlobGivingBot
from .config import Config
import config


log = logging.getLogger(__name__)


class NoWinnerFound(Exception):
    pass


class Giveaways:
    """Simple giveaway management commands."""

    def __init__(self, bot: BlobGivingBot):
        self.bot = bot

        self.config = Config('giveaways')
        self._giveaway_task = bot.loop.create_task(self.giveaway_loop())

    def __unload(self):
        self._giveaway_task.cancel()

    @property
    def emoji(self):
        return self.bot.get_emoji(config.giveaway_emoji)

    @property
    def channel(self):
        return self.bot.get_channel(config.giveaway_channel)

    @commands.command()
    async def giveaway(self, ctx: commands.Context, *, description: str):
        """Start a new Giveaway."""
        ends_at = ctx.message.created_at + config.giveaway_duration

        embed = discord.Embed(
            title=description,
            description=f'React with {self.emoji} to win!',
            color=discord.Color.magenta(),
            timestamp=ends_at,
        )
        embed.set_footer(text='Ends at')

        msg = await self.channel.send(embed=embed)
        await msg.add_reaction(self.emoji)

        await self.config.put(ends_at.timestamp(), msg.id)
        await ctx.send('Giveaway started!')

        if self._giveaway_task.done():
            self._giveaway_task = self.bot.loop.create_task(self.giveaway_loop())

    @commands.command()
    async def reroll(self, ctx: commands.Context, *, message_id: int):
        """Reroll a giveaway based on a message/giveaway ID."""
        try:
            message = await self.channel.get_message(message_id)
        except discord.NotFound:
            return await ctx.send(f'Couldn\'t find message with ID {message_id} in the giveaway channel!')

        # don't allow rerolling a giveaway which is running
        if message.created_at > ctx.message.created_at - config.giveaway_duration:
            return await ctx.send('This giveaway is still running! Rerolling can only be done after it has ended.')

        try:
            winner = await self.roll_user(message)
        except NoWinnerFound as e:
            await ctx.send(e)
        else:
            embed = message.embeds[0]
            giveaway_desc = embed.title

            embed.description = f'{winner.mention} is the new winner!'
            await message.edit(embed=embed)

            await ctx.send(f'Rerolled! {winner.mention} is the new winner for **{giveaway_desc}**!')

    async def giveaway_loop(self):
        # channels / emoji aren't loaded before being ready
        await self.bot.wait_until_ready()

        # run until Config.__len__ returns 0
        while self.config:
            # the keys of the config are unix timestamps so we can easily sort them
            oldest = min(self.config.all())

            until_end = float(oldest) - datetime.datetime.utcnow().timestamp()
            await asyncio.sleep(until_end)

            message_id = self.config.get(oldest)

            try:
                message = await self.channel.get_message(message_id)
            except discord.NotFound:
                # giveaways might be removed for moderation purposes, we don't want to post anything in this case
                log.warning(f'Couldn\'t find message associated with giveaway {message_id}, skipping')
                await self.config.remove(oldest)
                continue

            # prepare editing the embed
            embed = message.embeds[0]
            embed.set_footer(text='Ended at')

            # the name / title of this giveaway
            giveaway_desc = embed.title

            try:
                winner = await self.roll_user(message)
            except NoWinnerFound:
                embed.description = f'No one won this giveaway!'
                await message.edit(embed=embed)

                await self.channel.send(f'No winner found for **{giveaway_desc}**!')
            else:
                embed.description = f'{winner.mention} won this giveaway!'
                await message.edit(embed=embed)

                await self.channel.send(f'Congratulations {winner.mention}! You won **{giveaway_desc}**! DM <@489886869291794433> to claim your prize!')
            finally:
                await self.config.remove(oldest)

    async def roll_user(self, message: discord.Message) -> discord.Member:
        try:
            reaction = next(x for x in message.reactions if getattr(x.emoji, 'id', None) == self.emoji.id)
        except StopIteration:  # if a moderator deleted the emoji for some reason
            raise NoWinnerFound('Couldn\'t find giveaway emoji on specified message')

        users = await reaction.users().filter(lambda x: not x.bot).flatten()
        if not users:
            raise NoWinnerFound('No human reacted with the giveaway emoji on this message')
        else:
            return random.choice(users)


def setup(bot: BlobGivingBot):
    bot.add_cog(Giveaways(bot))
