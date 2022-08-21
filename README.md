<div align="center">

![johnny-chimpo.jpg](img/johnny-chimpo.jpg)

# mailchimp-ez
![Linux](https://img.shields.io/badge/linux-mint%2020.3-hotpink?logo=linux&logoColor=pink) ![Mac](https://img.shields.io/badge/mac-osx%2010.15-hotpink?logo=apple&logoColor=pink) ![Windows](https://img.shields.io/badge/windows-10-hotpink?logo=windows&logoColor=pink)

![GitHub Last Commit](https://img.shields.io/github/last-commit/presentformyfriends/mailchimp-ez?color=hotpink&logo=git&logoColor=pink) ![Python](https://img.shields.io/pypi/pyversions/selenium?color=hotpink&logo=python&logoColor=pink) [![Code style: black](https://img.shields.io/badge/style-black-000000.svg)](https://github.com/psf/black)

</div>

## Overview
Automatic email campaign with images and text using the Mailchimp API, written in Python for Linux, Mac OSX, and Windows.

Includes placeholder images and text, as well as an HTML template with responsive design.


## 📝 Usage

You need to have a [Mailchimp](https://mailchimp.com) account set up to use this Python script.

For the sake of clarity, the examples in this guide will assume you are cloning the repo to your home folder.

Clone the repo:
```
git clone https://github.com/presentformyfriends/mailchimp-ez.git
```

Configure the ```env.txt``` file to your custom environment variables, then rename the file to '.env' (minus quotes).

The ```.env``` file and the ```template.html``` file must both exist in the root folder for this script to work.

The best way to run this script is via the context menu:

```
animated.gif x3
```

To add this script to the context menu of your operating system, follow one of the examples below:

Linux
```
# ~/.local/share/nemo/actions/mailchimp-ez.nemo_action

[Nemo Action]
Active=true
Name=My Monthly Campaign
Comment=Create Mailchimp Campaign %e
Exec=python3 ~/mailchimp-ez/mailchimp-ez.py %F
Selection=notnone
Extensions=dir;
Icon-Name=mail-folder-sent
Quote=double
Terminal=true
```

Mac OSX 
```
Use Automator
```

Windows
```
; mailchimp-ez-context-menu.reg

[HKEY_CLASSES_ROOT\Directory\shell\mailchimp-ez]
"Icon"="C:\\Windows\\System32\\shell32.dll,326"

[HKEY_CLASSES_ROOT\Directory\shell\Meme Crop\command]
@="C:\\Users\\USERNAME\\AppData\\Local\\Programs\\Python\\Python39\\python.exe -i \"C:\\Users\\USERNAME\\mailchimp-ez.py\" \"%1\""
```

The ```template.html``` file uses JPG as the default image format. So either ensure that your images are all JPG, or you can change the HTML to accept PNG or GIF format. The Mailchimp API will only accept images in JPG, PNG, or GIF.

Images must be less than 1 MB in size or the Mailchimp API upload will fail silently. The ```check_image_size()``` function will raise an error and exit if any images exceed 1 MB in size.

Placeholder text is from [Hipster Ipsum](https://hipsum.co/).


## 🐍 Dependencies

### Packages
* [humanize](https://pypi.org/project/humanize/)
* [Selenium](https://pypi.org/project/selenium/)

### Frameworks
* [geckodriver](https://github.com/mozilla/geckodriver)

### Libraries
* [Jinja2](https://pypi.org/project/Jinja2/)
* [Mailchimp Marketing](https://github.com/mailchimp/mailchimp-marketing-python)

### Modules
* [base64](https://docs.python.org/3/library/base64.html)
* [datetime](https://docs.python.org/3/library/datetime.html)
* [os](https://docs.python.org/3/library/os.html#module-os)
* [pathlib](https://docs.python.org/3/library/pathlib.html)
* [pyautogui](https://github.com/asweigart/pyautogui)
* [shutil](https://docs.python.org/3/library/shutil.html)
* [sys](https://docs.python.org/3/library/sys.html)


## ⚖️ License

[![GitHub License](https://img.shields.io/github/license/presentformyfriends/mailchimp-ez?color=hotpink)](https://github.com/presentformyfriends/mailchimp-ez/blob/master/LICENSE)

