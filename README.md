<div align="center">

![johnny-chimpo.jpg](img/johnny-chimpo.jpg)

# mailchimp-ez
![Linux](https://img.shields.io/badge/linux-mint%2020.3-hotpink?logo=linux&logoColor=pink) ![Mac](https://img.shields.io/badge/mac-osx%2010.15-hotpink?logo=apple&logoColor=pink) ![Windows](https://img.shields.io/badge/windows-10-hotpink?logo=windows&logoColor=pink)

![GitHub Last Commit](https://img.shields.io/github/last-commit/presentformyfriends/mailchimp-ez?color=hotpink&logo=git&logoColor=pink) ![Python](https://img.shields.io/pypi/pyversions/selenium?color=hotpink&logo=python&logoColor=pink) [![Code style: black](https://img.shields.io/badge/style-black-000000.svg)](https://github.com/psf/black)

</div>

## Overview
Automatic email campaign with images and text using the Mailchimp API, written in Python for Linux, Mac OSX, and Windows.

Includes placeholder images and text, as well as an HTML template with responsive design.

After uploading your images and merging your HTML template, the script opens your browser, logs you into your Mailchimp account, and navigates to the newly created template. This is to give you the chance to check everything over. 

At this point, you can manually send the campaign via your browser. Or, if there is something you need to tweak, you can just leave it unsent and finish it later. You could also just delete it and start over if necessary.
<br><br>

## 📝 Usage

You need to have a [Mailchimp](https://mailchimp.com) account set up to use this Python script.

For the sake of clarity, the examples in this guide will assume you are cloning the repo to your home folder.

Clone the repo:
```
git clone https://github.com/presentformyfriends/mailchimp-ez.git
```

The YouTube video below will show you how to find your Mailchimp API key, server, segment ID, and list ID (Please be aware that what the YouTuber refers to as "Lists" in this video has now been changed to "Audiences" by Mailchimp):

[![mailchimp sub domain, api key, list id, segment id](https://img.youtube.com/vi/v8COddmNyPo/0.jpg)](https://www.youtube.com/watch?v=v8COddmNyPo)


Configure the ```env.txt``` file to your custom environment variables, then rename the file to '.env' (minus quotes).

The ```.env``` file and the ```template.html``` file must both exist in the root folder for this script to work.


The best way to run this script is via the context menu, i.e. right-click (or Control-click on Mac) on a folder that contains your images.

To add this python script to the context menu of your operating system, follow one of the examples below for your corresponding operating system.
<br><br>

### Linux
Copy and paste the code below into nano or vim and save as ```~/.local/share/nemo/actions/mailchimp-ez.nemo_action``` to create a Nemo Action (replace username with your own user name):
```
[Nemo Action]
Active=true
Name=My Monthly Campaign
Comment=Create Mailchimp Campaign %e
Exec=/usr/bin/python3 /home/username/mailchimp-ez/mailchimp-ez.py %F
Selection=notnone
Extensions=dir
Icon-Name=face-monkey-symbolic
Quote=double
Terminal=true
```
Make the ```mailchimp-ez.nemo_action``` file executable using the following command:
```
$ chmod +x ~/.local/share/nemo/actions/mailchimp-ez.nemo_action
```
To run, right-click on a folder that contains your images and select the action:

![usage.gif](img/linux-usage.gif)
<br><br>

### Mac OSX 
Open Automator and go to ```File``` > ```New``` > ```Quick Action```

In the Quick Action window, click on ```Utilities``` in the left pane, under ```Library```

In the adjacent pane, double-click ```Run AppleScript```

In the right pane, set ```Workflow receives current``` to ```folders``` in ```Finder.app```, set ```Image``` to ```Mail``` and set ```Color``` to ```Black```

Copy and paste the following code into the ```Run AppleScript``` section:

```
on run argv
	tell application "Terminal"
		activate
		do script "/usr/local/bin/python3 $HOME/mailchimp-ez/mailchimp-ez.py " & (quoted form of (POSIX path of (item 1 of argv))) in window 1
	end tell
end run
```
To run, control-click on a folder that contains your images, select ```Quick Actions``` and then select the action:

![usage.gif](img/mac-osx-usage.gif)
<br><br>

### Windows

Copy and paste the code below into Notepad and save as ```mailchimp-ez.reg```
```
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\shell\mailchimp-ez]
"Icon"="%SystemRoot%\\compstui.dll,64010"

[HKEY_CLASSES_ROOT\Directory\shell\mailchimp-ez\command]
@="%UserProfile%\\AppData\\Local\\Programs\\Python\\Python310\\python.exe -i \"%UserProfile%\\mailchimp-ez\\mailchimp-ez.py\" \"%1\""
```
Create a System Restore point and/or create a backup of your registry. Then double-click the ```mailchimp-ez.reg``` file to add the option to your context menu.

To run, right-click on a folder that contains your images and select the action:

![usage.gif](img/win-usage.gif)
<br><br>

### Other

The ```template.html``` file uses JPG as the default image format. So either ensure that your images are all JPG, or you can change the HTML to accept PNG or GIF format. The Mailchimp API will only accept images in JPG, PNG, or GIF.

Images must be less than 1 MB in size or the Mailchimp API upload will fail silently. The ```check_image_size()``` function will raise an error and exit if any images exceed 1 MB in size.

Placeholder text is from [Hipster Ipsum](https://hipsum.co/).
<br><br>

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
<br><br>

## ⚖️ License
[![GitHub License](https://img.shields.io/github/license/presentformyfriends/mailchimp-ez?color=hotpink)](https://github.com/presentformyfriends/mailchimp-ez/blob/master/LICENSE)

