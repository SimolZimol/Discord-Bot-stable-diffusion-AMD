__version__ = "0.6.5"
__all__ = ["Discordbot-stable_diffusion"]
__author__ = "SimolZimol"
__home_page__ = "https://github.com/SimolZimol/Discord-Bot-stable-diffusion-AMD-bot"

import discord
import os, sys
from discord.ext import commands
import asyncio
#import aiohttp
from discord.ext import tasks
import pathlib
import hashlib
import random
import numpy as np
import datetime
import time
from time import sleep
from diffusers import OnnxStableDiffusionPipeline
from diffusers.schedulers import DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler

TOKEN = 'put token here'
intents = discord.Intents.default()
intents.message_content = True
python = sys.executable

client = commands.Bot(command_prefix='-', intents=intents)#, owner_id = put your discord id here)
load = False


@client.event
async def on_ready():
    print('bot ready')
    await client.tree.sync()
    game = discord.Game("with the API") # you can change the bot activity here
    await client.change_presence(status=discord.Status.online , activity=game)


onnx_dir = 'PUT YOUR onnx folder here like C:/onnx_model/stable-diffusion-v1-4/'

lms = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear")

def load_onnx_model():
    global pipe
    pipe = OnnxStableDiffusionPipeline.from_pretrained(str(onnx_dir),
    safety_checker = None,
    provider="DmlExecutionProvider",
    scheduler =lms)
    print("ONNX pipeline is loadable")
    global prompt

def threaded_function(arg):
    for i in range(arg):
        print("running")
        sleep(1)

async def imgmake(ctx, prompt):  
        global load
        if (load == False):
            load_onnx_model()
            load = True 

        generator = np.random.RandomState(random.randint(0,4294967295))
        image = pipe(prompt,
                negative_prompt = None,
                num_inference_steps=30,
                height = 512,
                width = 512,
                guidance_scale=8.5,
                generator = generator,
                num_images_per_prompt = 1              
                ).images[0]
        basename = "Dml"
        suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        form = ".png"
        global filename
        filename = "_".join([basename, suffix, form])
        filename2 = "_".join([basename, suffix])
        global fp
        fp = "png/" + filename
        img_name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + ".png"
        image.save(f"{filename}")
        await ctx.send(file=discord.File(filename))            



@client.command()
async def creatimg(ctx, prompt):
    await ctx.typing()
    await imgmake(ctx, prompt)

# i will add more commands and functions later


client.run(TOKEN)
