__version__ = "0.7.3"
__all__ = ["Discordbot-stable_diffusion (Discord)"]
__author__ = "SimolZimol"
__home_page__ = "https://github.com/SimolZimol/Discord-Bot-stable-diffusion-AMD-bot"

import discord
import os, sys
from discord.ext import commands
import asyncio
#import aiohttp
from discord.ext import tasks
import pathlib
import numpy as np
from time import sleep
import subprocess
import threading
import concurrent.futures
import nest_asyncio

from image_generator import imgmake, load_onnx_model

TOKEN = '' # Discord token here

intents = discord.Intents.default()
intents.message_content = True
python = sys.executable

client = commands.Bot(command_prefix='-', intents=intents)#, owner_id = put your discord id here)
load = False

onnx_dir = pathlib.Path().absolute()/'onnx_models'
output_dir = pathlib.Path().absolute()/'output'
global prompt



executor = concurrent.futures.ThreadPoolExecutor()

def run_imgmake(prompt):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(imgmake(prompt))
    loop.close()
    return result

nest_asyncio.apply()

# Create a queue to store image generation requests
image_queue = asyncio.Queue()
loop = asyncio.get_event_loop()

async def process_image_queue():
    while True:
        # Wait for the next item in the queue
        prompt, channel, author, model = await image_queue.get()
        try:
            await channel.typing()
            
            # Run imgmake in a separate instance
            fp = run_imgmake(prompt)
            
            if fp is not None:
                file = discord.File(fp)
                message = await channel.send(f"Prompt: {prompt}\nAuthor: {author}\nModel: {model}", file=file)
                await message.add_reaction('🔄')  # Add a reaction for regenerating the image
            else:
                await channel.send("Unable to generate the image.")
        except Exception as e:
            print(f"Error processing image: {e}")
        finally:
            # Mark the task as done
            image_queue.task_done()

# Register the process_image_queue() coroutine as an event
@client.event
async def on_ready():
    loop.create_task(process_image_queue())
    print('Bot is ready!')
    print(f'Logged in as: {client.user.name}')
    print(f'Client ID: {client.user.id}')
    print('------')

@client.hybrid_command()
async def creatimg(ctx, *, prompt):
    # Add the image generation request to the queue
    await image_queue.put((prompt, ctx.channel, ctx.author, model_x))
    await ctx.send("Image generation request added to the queue.")


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    
    if reaction.emoji == '🔄':  # User reacted with the refresh emoji
        message = reaction.message
        if message.author == client.user:  # Check if the message was sent by the bot
            content = message.content
            prompt = content[8:content.index('\n')]  # Extract the prompt from the message content
            await image_queue.put((prompt, message.channel, user, model_x))
            await message.channel.send("Image generation request added to the queue.")


@client.hybrid_command()
async def load_model(ctx, model_):
    global model_x
    model_x = model_
    await ctx.typing()
    load_onnx_model(model_x)
    await ctx.send("Model loaded: " + model_x)

#@client.hybrid_command()
#async def download_model(ctx, xmodel_name):
#    await ctx.typing()
#    download_sd_model(xmodel_name)

# Run the event loop

# Run the event loop
try:
    loop.run_until_complete(client.start(TOKEN))
except KeyboardInterrupt:
    loop.run_until_complete(client.logout())
finally:
    loop.close()
