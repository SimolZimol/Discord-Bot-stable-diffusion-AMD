import gradio as gr
from huggingface_hub import _login
from huggingface_hub.hf_api import HfApi, HfFolder
import subprocess
import sys
import pathlib
import importlib.util
import numpy as np
import random
import datetime
from PIL import Image
#from modules import txt2img
from diffusers import OnnxStableDiffusionPipeline

python = sys.executable
#repositories = pathlib.Path().absolute() / 'repositories'

onnx_dir = pathlib.Path().absolute()/'onnx_models'



def huggingface_login(token):
    try:
        #output = _login._login(HfApi(), token = token)
        output = _login._login(token = token, add_to_git_credential = True)
        return "Login successful."
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

    
#'CompVis/stable-diffusion-v1-4'


def display_onnx_models():
    if not onnx_dir.exists():
        onnx_dir.mkdir(parents=True, exist_ok=True)
    return [m.name for m in onnx_dir.iterdir() if m.is_dir()]


def start_app():
    with gr.Blocks() as app:
        gr.Markdown('STABLE DIFFUSION WEBUI FOR AMD')
        with gr.Tab('Model Manager'):
            gr.Markdown("Some of the models require you logging in to Huggingface and agree to their terms. Make sure to do that before downloading models!")
            model_download_input = gr.Textbox()
            model_download_button = gr.Button('Download Model')
            model_dir_refresh = gr.Button('Refresh')
            
        with gr.Tab('Settings'):
            gr.HTML("Click on this link to find your <a href='https://huggingface.co/settings/tokens' style='color:blue'>Huggingface Access Token</a>")
            hugginface_token_input = gr.Textbox()
            huggingface_login_message = gr.Textbox()
            huggingface_login_button = gr.Button('Login HuggingFace')

        huggingface_login_button.click(huggingface_login,
                                       inputs = hugginface_token_input,
                                       outputs = huggingface_login_message)
        
        model_download_button.click(download_sd_model, inputs = model_download_input)
        
        #load_onnx_model_button.click(load_onnx_model, inputs=txt2img_model_input, show_progress=True, outputs = test_output)


    app.launch(inbrowser = True)


if __name__ == "__main__":
    start_app()
