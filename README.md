# 	KonoSuba: Fantastic Days asset downloader

A small project that downloads all assets of the global version of KonoSuba: Fantastic Days and extracts them while it's at it.

The script updates the assets and even its own parameters on its own,
so all you have to do is execute the download_assets.py script after every update to get the latest files.

## Script Requirements

The ``download_assets_old.py`` script extracts the relevant data from the latest apk found on QooApp.
Since the resource request also return the latest configuritions this isn't strictly necessary,
so the ``download_assets.py`` script can do without the trouble, but might run into trouble if something changes.

So, only run ``download_assets_old.py`` IF ``download_assets.py`` doesnisn't able to update.

### old and new

- Python 3.6+
- JRE (Java Runtime Environment) for backsmali [for the old version]

- UnityPy 1.7.10
- requests

```cmd
pip install UnityPy==1.7.10
pip install requests
```

## Master

The ``update_master.py`` script downloads the laster master failes from the game server and decrypts them.

## TODO

- add japanese and chinese versions
