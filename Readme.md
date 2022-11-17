# CS3103 Proxy

A proxy with extensions

## Requirements

1. Python 3 > 3.8

## Usage

```bash
python proxy <port> <img_sub_mode> <atk_mode>
```

For more information please use `python proxy -h` to see the full list of options.

## Image Substitution Mode

In Image substitution mode, the proxy will substitute images which are loaded with the image at the url defined in `./proxy/Proxy/constants.py`

## Attack Mode

Whenever a request is sent to the URL, the proxy will reply with the string `“You are being attacked”` instead of the actual content
