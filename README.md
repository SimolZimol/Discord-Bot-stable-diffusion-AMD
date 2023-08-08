# Discordbot-diffuser (AMD)

| Version | Supported          |
| ------- | ------------------ |
| AMD GPU | :white_check_mark: |
| Nvidia GPU  | :x: |
| AMD CPU |:white_check_mark: |
| Intel CPU |❓ |

## System Requirements
+ Python 3.7 , 3.8 , 3.9 or 3.10 (https://www.python.org/)
+ you will need git (https://git-scm.com/downloads)

## How to install

At the moment you need to get an ready to use onnx model, put your onnx model in the onnx_model folder. 
First, the tokens must be inserted in the bot.py file.
The Discord bot token is the most important part, without it the bot cannot start. The other token for huggingface is only used to download new models and is not needed for the basic functions. After inserting the Discord bot token, you can now execute the start.bat. After installing the requirements, the bot should start and "bot ready" should appear in the console. After the bot has been started, just load the model with the command /load_model modelname or -load_model model-name after this has been done successfully, the bot should now be able to make pictures. 

Information the model must be reloaded every time the bot is restarted (/load_model model-name)

if you need help dm me on discord for help (**simolzimol**)

## How to use
Commands
+ -download_model modeladress (coming soon)
+ -load_model model-name
+ /load_model model-name
+ -creatimg "prompt"
+ /creatimg prompt


![grafik](https://github.com/SimolZimol/Discord-Bot-stable-diffusion-AMD/assets/70102430/069879ac-a172-4bb2-880a-ac0c2bc6b8cf)

