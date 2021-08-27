# 	KonoSuba: Fantastic Days asset downloader

A small project that downloads all assets of the global version of KonoSuba: Fantastic Days and extracts them while it's at it.

The script updates the assets and even its own parameters on its own,
so all you have to do is execute the download_assets.py script after every update to get the latest files.

## Script Requirements

- Python 3.6+

- UnityPy 1.7.10
- requests

```cmd
pip install UnityPy==1.7.10
pip install requests
```

## Master

The ``master`` folder contains all the master data of the game.
This data is requests from the game api in an encrypted format, the folder in this repo contains them decrypted.
The decryption function won't be shared for the time being.

## TODO

- add japanese and chinese versions