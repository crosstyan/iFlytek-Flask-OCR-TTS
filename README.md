# Flask Web Application based on OCR TTS of iFlytek
The project is a demo for OCR and TTS, which use the iFlytek API, running in Flask
## Requirement
`Python 3.6+` (Tested on `Python 3.6` and `Python 3.8`)
Of course `venv` or `virtualenv` are accepted
```
astroid==2.4.1
Bootstrap-Flask==1.3.2
certifi==2020.4.5.1
cffi==1.14.0
chardet==3.0.4
click==7.1.2
colorama==0.4.3
Flask==1.1.2
Flask-WTF==0.14.3
gevent==20.5.2
greenlet==0.4.16
idna==2.9
isort==4.3.21
itsdangerous==1.1.0
Jinja2==2.11.2
lazy-object-proxy==1.4.3
MarkupSafe==1.1.1
mccabe==0.6.1
Pillow==7.1.2
pycparser==2.20
pylint==2.5.2
python-dotenv==0.13.0
requests==2.23.0
six==1.15.0
toml==0.10.1
urllib3==1.25.9
websocket==0.2.1
websocket-client==0.57.0
Werkzeug==1.0.1
wrapt==1.12.1
WTForms==2.3.1
zope.event==4.4
zope.interface==5.1.0
```
use`pip install -r requirements.txt` to install all of the dependency. 
## Usage
### Configure
Rename `application/config.demo.py` to `config.py`. and fill the `OCR_KEY`, `TTS_KEY`, `TTS_SECRET` and `APPID`, which you can get from [iFlytek](https://www.xfyun.cn/)
### Start
You're directory tree should look like this
```
├── application
│   ├── config.py
│   ├── __init__.py
│   ├── route.py
│   ├── static
│   │   ├── audio
│   │   ├── css
│   │   │   └── stylesheet.css
│   │   └── image
│   └── templates
│       ├── base.html
│       ├── index.html
│       └── view.html
├── app.py
└── requirements.txt
```
```bash
flask run
```
Or uWSGI, or any WSGI compatible web server. 
## Demo
Here's a [demo site](http://ai.nyan.one/)
## License
```
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
  ```