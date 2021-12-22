import os
from dotenv import load_dotenv
import logging
import discord
from discord.ext import commands
import matching
from PIL import Image
import io
from game import Game
import pickle
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
load_dotenv()


EMOJI_MAX_SIZE = (200, 200)


class MatchMaker(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            with open("games.pkl", "rb") as f:
                self.games = pickle.load(f)
        except:
            self.games = {}
        print(self.games)

    async def on_ready(self):
        print(f"logged as {self.user.name}, {self.user.id}")


bot = MatchMaker(command_prefix="`")


class MatchButton(discord.ui.View):
    @discord.ui.button(style=discord.ButtonStyle.blurple, label='Go!')
    async def click_me_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        message = discord.utils.get(bot.cached_messages, id=interaction.message.id)
        reactions = message.reactions
        requests = defaultdict(lambda: set())  # user -> set(games willing to play)
        for reaction in reactions:
            game_name = reaction.emoji.name
            if reaction.count > 1:
                for user in await reaction.users().flatten():
                    if user.id != bot.user.id:
                        requests[user].add(bot.games[game_name])

        results = matching.match(requests)
        out_string = ""
        for i, (score, result_dict) in enumerate(results):
            out_string += f"======OPTION {i+1}======\n"
            for game in result_dict:
                if len(result_dict[game]) > 0:
                    emoji = discord.utils.get(interaction.guild.emojis, name=game.name)
                    out_string += f"{emoji} {len(result_dict[game])}\n"
                    for user in result_dict[game]:
                        out_string += user.display_name + " "
                    out_string += "\n"
        await interaction.response.send_message(out_string)


@bot.command()
async def match(ctx):
    msg = await ctx.send("Game?!", view=MatchButton())
    try:
        for game in bot.games:
            emoji = discord.utils.get(ctx.guild.emojis, name=game)
            await msg.add_reaction(emoji)
    except:
        logging.error("Error, couldn't add reaction to message")


@bot.command()
async def add(ctx, name, players):
    if len(ctx.message.attachments) > 0:
        logging.info(f"Adding {name}")

        # read, download, and upload image
        img = Image.open(io.BytesIO(await ctx.message.attachments[0].read()))
        img.thumbnail(EMOJI_MAX_SIZE, Image.ANTIALIAS)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")

        await ctx.guild.create_custom_emoji(name=name, image=img_bytes.getvalue(), reason="Matchmaker")
        game = Game(name, players)
        bot.games[name] = game

        logging.info(f"Added {game}")
        emoji = discord.utils.get(ctx.guild.emojis, name=name)
        await ctx.send(f"Added {emoji} {game}")
        with open("games.pkl", "wb") as f:
            pickle.dump(bot.games, f)


@bot.command()
async def games(ctx):
    out_string = ""
    for game in bot.games:
        emoji = discord.utils.get(ctx.guild.emojis, name=game)
        out_string += f"{emoji} {bot.games[game]}\n"
    await ctx.send(out_string)


@bot.command()
async def remove(ctx, game):
    if game in bot.games:
        emoji = discord.utils.get(ctx.guild.emojis, name=game)
        await ctx.guild.delete_emoji(emoji)
        del bot.games[game]
        with open("games.pkl", "wb") as f:
            pickle.dump(bot.games, f)
        await ctx.send(f"Removed {game} from roster")
    else:
        await ctx.send(f"{game} not in roster")


bot.run(os.getenv("TOKEN"))

