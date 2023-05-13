__version__ = "0.7.3"
__all__ = ["Discordbot-stable_diffusion"]
__author__ = "SimolZimol"
__home_page__ = "https://github.com/SimolZimol/Discord-Bot-stable-diffusion-AMD-bot"

import discord
import os, sys
from discord.ext import commands
import asyncio
#import aiohttp
from discord.ext import tasks
from huggingface_hub import _login
import pathlib
import hashlib
import random
import numpy as np
import datetime
import time
import subprocess
from time import sleep
from diffusers import OnnxStableDiffusionPipeline
from diffusers.schedulers import DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler

TOKEN = '' #Discord Token here
token = '' #huggingface token here



intents = discord.Intents.default()
intents.message_content = True
python = sys.executable

client = commands.Bot(command_prefix='-', intents=intents)#, owner_id = put your discord id here)
load = False

onnx_dir = pathlib.Path().absolute()/'onnx_models'
output_dir = pathlib.Path().absolute()/'output'
global model_
global prompt

@client.event
async def on_ready():
    print('bot ready')
    await client.tree.sync()
    game = discord.Game("with the API") # you can change the bot activity here
    await client.change_presence(status=discord.Status.online , activity=game)

lms = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear")

def load_onnx_model(model_):
    global pipe
    pipe = OnnxStableDiffusionPipeline.from_pretrained(str('onnx_models/' + model_),
    provider="DmlExecutionProvider",
    scheduler =lms)
    global load
    load = True 
    print("ONNX pipeline is loadable")



def threaded_function(arg):
    for i in range(arg):
        print("running")
        sleep(1)

async def imgmake(ctx, prompt):  

    if (load == True):
            
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
    else:
        print("ONNX not ready")
    

def pip_install(lib):
    subprocess.run(f'echo Installing {lib}...', shell=True)
    if 'ort_nightly_directml' in lib:
        subprocess.run(f'echo 1', shell=True)
        subprocess.run(f'echo "{python}" -m pip install {lib}', shell=True)
        subprocess.run(f'"{python}" -m pip install {lib} --force-reinstall', shell=True)
    else:
        subprocess.run(f'echo 2', shell=True)
        subprocess.run(f'echo "{python}" -m pip install {lib}', shell=True, capture_output=True)
        subprocess.run(f'"{python}" -m pip install {lib}', shell=True, capture_output=True)          

def pip_uninstall(lib):
    subprocess.run(f'echo Uninstalling {lib}...', shell=True)
    subprocess.run(f'"{python}" -m pip uninstall -y {lib}', shell=True, capture_output=True)

def huggingface_login(token):
    try:
        #output = _login._login(HfApi(), token = token)
        output = _login._login(token = token, add_to_git_credential = True)
        return "Login successful."
    except Exception as e:
        return str(e)

def download_sd_model(model_path):
    pip_install('onnx')
    from src.diffusers.scripts import convert_stable_diffusion_checkpoint_to_onnx
    onnx_opset = 14
    onnx_fp16 = False
    try:
        model_name = model_path.split('/')[1]
    except:
        model_name = model_path
    onnx_model_dir = onnx_dir/model_name 
    if not onnx_dir.exists():
        onnx_dir.mkdir(parents=True, exist_ok=True)
        print(model_name)
    convert_stable_diffusion_checkpoint_to_onnx.convert_models(model_path, str(onnx_model_dir), onnx_opset, onnx_fp16)
    pip_uninstall('onnx')

@client.command()
async def creatimg(ctx, prompt):
    await ctx.typing()
    await imgmake(ctx, prompt)

@client.command()
async def Load_Model(ctx, model_):
    await ctx.typing()
    load_onnx_model(model_)
    ctx.send("ready !")

#@client.command()
#async def download_model(ctx, xmodel_name):
#    await ctx.typing()
#    download_sd_model(xmodel_name)




client.run(TOKEN)
