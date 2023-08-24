__version__ = "0.6.8"
__all__ = ["Discordbot-stable_diffusion (Bot part)"]
__author__ = "SimolZimol"
__home_page__ = "https://github.com/SimolZimol/Discord-Bot-stable-diffusion-AMD-bot"

import os, sys
import asyncio
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
from huggingface_hub import _login
from huggingface_hub.hf_api import HfApi, HfFolder
import importlib.util


onnx_dir = pathlib.Path().absolute() / 'onnx_models'
output_dir = pathlib.Path().absolute() / 'output'
global model_
global prompt
load = False
python = sys.executable

lms = LMSDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear", steps_offset=3)
def load_onnx_model(model_):
    global pipe
    pipe = OnnxStableDiffusionPipeline.from_pretrained(str('onnx_models/' + model_),
    provider="DmlExecutionProvider",
    scheduler =lms)
    global load
    load = True 
    print("ONNX pipeline is loadable")

async def imgmake(prompt, negativeprompt: str = None):  

    if (load == True):
            
        generator = np.random.RandomState(random.randint(0,4294967295))
        image = pipe(prompt,
                negative_prompt = negativeprompt,
                num_inference_steps=25,
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
        image.save(output_dir/filename)
        return str(output_dir/filename)
    else:
        print("ONNX not ready")
    

onnx_dir = pathlib.Path().absolute()/'onnx_models'
output_dir = pathlib.Path().absolute()/'output'


def download_sd_model(model_path):
    pip_install('onnx')
    from conv import convert_models
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
    convert_models(model_path, str(onnx_model_dir), onnx_opset, onnx_fp16)
    pip_uninstall('onnx')

def huggingface_login(token):
    try:
        #output = _login._login(HfApi(), token = token)
        output = _login._login(token = token, add_to_git_credential = True)
        return True
    except Exception as e:
        return str(e)

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

def is_installed(lib):
    library =  importlib.util.find_spec(lib)
    return (library is not None)
