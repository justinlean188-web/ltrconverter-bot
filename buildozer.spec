[app]

# (str) Title of your application
title = LTR Converter Bot

# (str) Package name
package.name = ltrconverter

# (str) Package domain (needed for android/ios packaging)
package.domain = com.ltrconverter.bot

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,requests,telebot,flask,werkzeug,urllib3,certifi,charset-normalizer,idna,click,itsdangerous,jinja2,markupsafe,pyyaml,pytelegrambotapi,telegram,httpx,aiosignal,anyio,asyncio,attrs,backoff,charset-normalizer,fastapi,h11,httpcore,multidict,pydantic,starlette,typing-extensions,yarl,aiogram,aiosignal,anyio,asyncio,attrs,backoff,charset-normalizer,fastapi,h11,httpcore,multidict,pydantic,starlette,typing-extensions,yarl,aiogram

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (list) List of service to declare
services = 

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
# orientation = portrait  # Duplicate removed

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#[app]
#source.exclude_patterns = license,images/*/*.jpg
#
#    This can be translated into:
#
#[app:source.exclude_patterns]
#license
#images/*/*.jpg

#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#[app@demo]
#title = My Application (demo)
#
#[app:source.exclude_patterns@demo]
#images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
#buildozer --profile demo android debug
