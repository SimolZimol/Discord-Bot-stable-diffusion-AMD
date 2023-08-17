__version__ = "dev-0.8.6"
__all__ = ["Discordbot-stable_diffusion (Discord)"]
__author__ = "SimolZimol"
__home_page__ = "https://github.com/SimolZimol/Discord-Bot-stable-diffusion-AMD-bot"

import discord
import os, sys
from discord.ext import commands
import asyncio
import pathlib
import numpy as np
from time import sleep

import concurrent.futures
import nest_asyncio
import requests
from typing import Literal , List

from discord import app_commands
from image_generator import imgmake, load_onnx_model, download_sd_model , huggingface_login
import pprint
import onnxruntime

pprint.pprint(onnxruntime.get_available_providers())

TOKEN = ''
token_huggingface = ''

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
python = sys.executable

client = commands.Bot(command_prefix='-', intents=intents)
load = False

onnx_dir = pathlib.Path().absolute()/'onnx_models'
output_dir = pathlib.Path().absolute()/'output'
models_list = [folder for folder in os.listdir(onnx_dir) if os.path.isdir(os.path.join(onnx_dir, folder))]
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

        # Version check
    version_url = "https://simolzimol.eu/version.txt"
    current_version = __version__

    try:
        response = requests.get(version_url)
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version != current_version:
                print(f"New version available: {latest_version}")
            else:
                print("Bot is up to date.")
        else:
            print("Unable to retrieve version information.")
    except requests.exceptions.RequestException:
        print("Failed to connect to version server.")


        

@client.hybrid_command(with_app_command=True)
async def creatimg(ctx, *, prompt):
    # Add the image generation request to the queue
    await image_queue.put((prompt, ctx.channel, ctx.author, model_x))
    await ctx.send("Image generation request added to the queue.")
@app_commands.describe(
    prompt='How do you want to look your image for example "house , lake, woods"',
)

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

@client.hybrid_command(with_app_command=True)
async def load_model(ctx,model_ : str):
    if model_ in models_list:
        global model_x
        model_x = model_
        await ctx.typing()
        load_onnx_model(model_x)
        await ctx.send("Model loaded: " + model_x)
    else:
        await ctx.send("Invalid model name. Available models: " + ", ".join(models_list))
@app_commands.describe(
    model_='The model_ you want to load',
)

@client.hybrid_command(with_app_command=True)
async def download_model(ctx, model_download_input):
    await ctx.typing()    
    test_ = huggingface_login(token_huggingface)
    if test_ == True:

        download_sd_model(model_download_input)
        await ctx.send("Model downloaded: " + model_download_input)
    else :
        await ctx.send("Model download failed")


try:
    loop.run_until_complete(client.start(TOKEN))
except KeyboardInterrupt:
    loop.run_until_complete(client.logout())
finally:
    loop.close()
