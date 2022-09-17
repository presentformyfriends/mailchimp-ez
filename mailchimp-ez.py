#!/usr/bin/python3

import os
import shutil
import sys
import pyautogui
import humanize
import logging
import jinja2
import time
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from pathlib import Path
from datetime import datetime
from base64 import b64encode
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from dotenv import load_dotenv


def copy_images(home_path, source_path):
    if source_path.is_dir():
        print("Preparing to add images from: " + str(source_path) + "\n")
        input("Press Enter to continue ...")
        # Create destination dir, overwrite if it already exists
        destination_path = home_path / "Documents/campaign"
        try:
            destination_path.mkdir()
        except FileExistsError:
            shutil.rmtree(destination_path)
            destination_path.mkdir()
        print("\nCreated directory " + str(destination_path) + "\n")
        # Check file size of images, reject if any are over 1 MB
        for image in sorted(source_path.glob("*")):
            if image.is_file() and (image.name).endswith(".jpg"):
                image_size = os.stat(image).st_size
                if image_size <= 1048576:
                    shutil.copy(image, destination_path)
                    print(str(image) + " copied")
                else:
                    natural_image_size = humanize.naturalsize(image_size)
                    print(
                        "Could not add "
                        + file_path.name
                        + " file size too large: "
                        + natural_image_size
                    )
                    print("\nImages must be 1 MB or less\n")
                    input("Press Enter to quit ...")
                    sys.exit()

        print("\nSource path:", source_path)  # Source dir
        print("Destination path:", destination_path)  # Destination dir
        return destination_path  # Return destination dir

    elif source_path.is_file():
        print("Invalid selection: path must be directory, not file\n")
        input("Press Enter to quit ...")
        sys.exit()


def create_HTML(home_path, source_path, destination_path):
    outputfile = destination_path / "render.html"

    text1 = "Vinyl normcore migas sustainable before they sold out Brooklyn fit air plant whatever salvia vape. Distillery jean shorts banjo helvetica meh umami kale chips asymmetrical shabby chic bicycle rights knausgaard. VHS hexagon JOMO salvia mlkshk, listicle man bun vegan biodiesel. Leggings taxidermy gluten-free glossier biodiesel, green juice ethical kinfolk JOMO slow-carb pinterest."

    text2 = "Glossier neutra cardigan selvage, bitters raclette hammock. Single-origin coffee cloud bread meggings fashion axe master cleanse glossier, austin listicle edison bulb shoreditch. Celiac small batch hell of chia paleo raclette praxis literally tumeric tousled mustache fingerstache pinterest. Jianbing cloud bread gentrify, poke raclette etsy offal sustainable dreamcatcher banh mi humblebrag. Cardigan portland health goth migas, truffaut tousled tote bag sriracha pour-over humblebrag hella praxis YOLO. Roof party sartorial snackwave edison bulb tote bag. Heirloom edison bulb live-edge letterpress."

    text3 = "Four loko air plant whatever gastropub heirloom jianbing. Praxis meditation viral lyft humblebrag, pug butcher irony ennui ramps selvage DSA street art shabby chic. Hella unicorn XOXO sus pitchfork. Thundercats vexillologist tumblr mukbang sus meggings. Heirloom knausgaard succulents gentrify gastropub snackwave sartorial."

    # Rename images to numbered filenames, define data for subs in template
    image_count = 1
    data = []
    for image in sorted(destination_path.glob("*")):
        target = Path(destination_path / "image{:n}.jpg".format(image_count))
        image = image.rename(target)
        data += [
            (
                image.name,
                "This is image number {:n}".format(image_count),
                "text{:n}".format(image_count),
            )
        ]
        image_count += 1

    try:
        root_path = home_path / "mailchimp-ez"
        subs = (
            jinja2.Environment(loader=jinja2.FileSystemLoader(root_path))
            .get_template("template.html")
            .render(mydata=data)
        )
    except FileNotFoundError:
        print("template.html file not found")
        input("Press Enter to quit ...")
        sys.exit()

    # Write substitutions to new file
    with open(outputfile, "w") as f:
        f.write(subs)


def create_archive(destination_path):
    if "render.html" in os.listdir(destination_path):
        date_stamp = datetime.now().strftime("%Y-%m-%d")
        filename = destination_path.parent / (
            date_stamp + "_" + destination_path.name
        )
        archive = shutil.make_archive(
            filename, "zip", destination_path
        )  # args = (base_name, format, root_dir)
        archive_path = Path(archive)
        print("\nCreated " + archive_path.name + "\n")
        return archive_path
    else:
        print("render.html file not found")
        input("Press Enter to quit ...")
        sys.exit()


def encode_archive(archive_path):
    if archive_path.is_file() and str(archive_path).endswith(".zip"):
        try:
            print("Encoding " + archive_path.name + " to utf-8\n")
            with open(archive_path, "rb") as archive:
                return b64encode(archive.read()).decode("utf-8")
        except FileNotFoundError:
            print("Encoding of " + archive_path.name + " FAILED")
            sys.exit()
    else:
        print("Invalid archive file")
        input("Press Enter to quit ...")
        sys.exit()


def get_client(api_key, server_code):
    try:
        client = MailchimpMarketing.Client()
        client.set_config({"api_key": api_key, "server": server_code})
        return client
    except ApiClientError as error:
        print("Client Error: {}".format(error.text))
        input("Press Enter to quit ...")
        sys.exit()


def get_health_status(client):
    """
    Check health status
    Response should be: {'health_status': "Everything's Chimpy!"}
    """
    response = client.ping.get()
    if response == {"health_status": "Everything's Chimpy!"}:
        print("Response: {}".format(response) + "\n")
    else:
        print("Invalid health status")
        input("Press Enter to quit ...")
        sys.exit()


def get_response(
    client, segment_id, list_id, subject, title, from_name, reply_to_email
):
    """Get response from API"""
    try:
        campaign_response = client.campaigns.create(
            {
                "type": "regular",
                "recipients": {
                    "segment_opts": {"saved_segment_id": segment_id},
                    "list_id": list_id,
                },
                "settings": {
                    "subject_line": subject,
                    "title": title,
                    "from_name": from_name,
                    "reply_to": reply_to_email,
                },
            }
        )
        return campaign_response
    except ApiClientError as error:
        print("Error Creating Campaign: {}".format(error.text))
        input("Press Enter to quit ...")
        sys.exit()


def get_campaign_id(campaign_response):
    """Grab Campaign ID"""
    try:
        campaign_id = str(campaign_response["id"])
        print("CAMPAIGN ID: " + campaign_id)
        return campaign_id
    except ApiClientError as error:
        print("Campaign ID Error: {}".format(error.text))
        input("Press Enter to quit ...")
        sys.exit()


def get_web_id(campaign_response):
    """Grab Web ID"""
    try:
        web_id = str(campaign_response["web_id"])
        print("WEB ID: " + web_id)
        return web_id
    except ApiClientError as error:
        print("Web ID Error: {}".format(error.text))
        input("Press Enter to quit ...")
        sys.exit()


def set_content(client, campaign_id, encoded_archive_data):
    """Set campaign content"""
    try:
        content = client.campaigns.set_content(
            campaign_id,
            {
                "archive": {
                    "archive_content": encoded_archive_data,
                    "template": {"id": 0},
                    "html": "template.html",
                }
            },
        )
    except ApiClientError as error:
        print("ID Error: {}".format(error.text))
        input("Press Enter to quit ...")
        sys.exit()


def remove_dir(delete_path):
    if os.path.isdir(delete_path):
        shutil.rmtree(delete_path)  # Remove destination dir
        print("\nRemoved directory " + str(delete_path) + "\n")
        input("Press Enter to login to Mailchimp website ...")


def driver_config(geckodriver_path):
    service = Service(geckodriver_path, log_path=os.path.devnull)
    driver = webdriver.Firefox(service=service)
    return driver


def load_website(
    driver,
    username,
    password,
    server_code,
    question1,
    question2,
    question3,
    answer1,
    answer2,
    answer3,
):
    print("\nLoading Mailchimp website with Selenium driver ...")

    driver.maximize_window()  # Maximize browser window

    driver.get("https://login.mailchimp.com")  # Load Mailchimp site

    # Wait for footer banner close button
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@aria-label='Close']")
            )
        ).click()
    except (
        NoSuchElementException,
        TimeoutException,
        ElementClickInterceptedException,
    ):
        print("Close button not located")

    # Enter username
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
        ).send_keys(username)
        time.sleep(1)
    except (NoSuchElementException, TimeoutException):
        print("Couldn't locate username field")
        input("Press Enter to quit ...")
        sys.exit()

    # Enter password
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#password"))
        ).send_keys(password)
        time.sleep(1)
    except (NoSuchElementException, TimeoutException):
        print("Couldn't locate password field")
        input("Press Enter to quit ...")
        sys.exit()

    # Click 'Log In' button, try again if unable to locate button
    while True:
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#submit-btn")
                )
            ).click()
            time.sleep(1)
            break
        except (
            NoSuchElementException,
            TimeoutException,
            ElementClickInterceptedException,
        ):
            print("Couldn't press Log In button")
            continue

    # Wait for URL to change, try again if it doesn't
    while True:
        try:
            WebDriverWait(driver, 20).until(
                EC.url_changes("https://login.mailchimp.com/")
            )
            print("URL changed")
            break
        except:
            print("URL did not change")
            continue

    # Click radio button, try again if unable to locate button
    while True:
        try:
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "#dijit_form_RadioButton_1")
                )
            ).click()
            time.sleep(1)
            break
        except (
            NoSuchElementException,
            TimeoutException,
            ElementClickInterceptedException,
        ):
            print("Could not click radio button")
            continue

    # Get security question, try again if unable to locate question
    while True:
        try:
            question = (
                WebDriverWait(driver, 15)
                .until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "//div[@class='radio-description-out question-input fs-mask']/div/p",
                        )
                    )
                )
                .text
            )
            time.sleep(1)
            break
        except (NoSuchElementException, TimeoutException):
            print("Could not answer security question")
            continue

    # Locate answer field for security question
    # Send the correct answer for the matching question
    while True:
        try:
            answer_field = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//input[@id='question_answer']")
                )
            )
            if question == question1:
                answer_field.send_keys(answer1)
            elif question == question2:
                answer_field.send_keys(answer2)
            elif question == question3:
                answer_field.send_keys(answer3)
            else:
                print("Security question not recognized")
                input("Press Enter to quit ...")
                sys.exit()
            time.sleep(1)
            break
        except (NoSuchElementException, TimeoutException):
            print("Could not answer security question")
            continue

    # Wait for "Submit Verification" button then click it
    while True:
        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//button[text()=' Submit Verification ']")
                )
            ).click()
            time.sleep(1)
            break
        except (
            NoSuchElementException,
            TimeoutException,
            ElementClickInterceptedException,
        ):
            print("Could not press Submit Verification button")
            continue

    # Wait for URL to change
    while True:
        try:
            WebDriverWait(driver, 20).until(
                EC.url_changes(
                    "https://"
                    + server_code
                    + ".admin.mailchimp.com/login/verify/"
                )
            )
            print("URL changed")
            time.sleep(1)
            break
        except:
            print("URL did not change")
            continue

    # Mitigate for "Updates to our Terms" page
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[text()='Remind me later']")
            )
        ).click()
        print("Skipped Mailchimp update page")
    except (
        NoSuchElementException,
        TimeoutException,
        ElementClickInterceptedException,
    ):
        print("No Mailchimp update page detected")
        pass

    # Wait for Campaigns link then click it
    while True:
        try:
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//nav/ul/li/button/div/span[text()='Campaigns']",
                    )
                )
            ).click()
            time.sleep(1)
            break
        except (
            NoSuchElementException,
            TimeoutException,
            ElementClickInterceptedException,
        ):
            print("Could not click on Campaigns dropdown")
            continue

    # Wait for link with current Web ID then click it
    while True:
        try:
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@aria-label='All campaigns']")
                )
            ).click()
            time.sleep(1)
            break
        except (
            NoSuchElementException,
            TimeoutException,
            ElementClickInterceptedException,
        ):
            print("Could not click on All Campaigns link")
            continue

    # Wait for user to send campaign and press ENTER to quit
    input(
        "\nYou can check over your campaign and send it now\n\nOnce you have sent your campaign, press Enter to quit ..."
    )

# Define home path
home_path = Path.home()

# ENVIRONMENT VARIABLES #

load_dotenv()  # Load environment variables

# Credentials
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
api_key = os.environ.get("API_KEY")
server_code = os.environ.get("SERVER_CODE")  # Example: us17
segment_id = os.environ.get("SEGMENT_ID")  # Example: 3986147
list_id = os.environ.get("LIST_ID")  # Example: 04c27d6ja5

# Security Questions
# MailChimp requires you to choose three security questions
# You can change the questions in '.env' to match your choices
question1 = os.environ.get("QUESTION1")
question2 = os.environ.get("QUESTION2")
question3 = os.environ.get("QUESTION3")

# Security Answers
answer1 = os.environ.get("ANSWER1")
answer2 = os.environ.get("ANSWER2")
answer3 = os.environ.get("ANSWER3")

# Define geckodriver path #
# Change this path to wherever your geckodriver resides
geckodriver_path = home_path / "Downloads/geckodriver"

# Subject and Title
month = datetime.now().strftime("%B")  # Define month
year = datetime.now().strftime("%Y")  # Define year
subject = (
    "Monthly Mailchimp Campaign " + month.upper() + " " + year
)  # Email subject
title = "My Mailchimp Campaign " + month.upper() + " " + year  # Title

# From name and reply-to email address
from_name = "Kelly Kapoor"
reply_to_email = "k.kapoor@dundermifflin.com"


# MAIN #

home_path = Path.home()
source_path = Path(sys.argv[1])  # Define user's chosen dir as source path
destination_path = copy_images(
    home_path, source_path
)  # Copy images from user's chosen dir to destination dir
create_HTML(home_path, source_path, destination_path)  # Render the HTML file
archive_path = create_archive(destination_path)  # Create archive
encoded_archive_data = encode_archive(archive_path)  # Encode archive to base64
client = get_client(api_key, server_code)
get_health_status(client)  # Health status check
campaign_response = get_response(
    client, int(segment_id), list_id, subject, title, from_name, reply_to_email
)
campaign_id = get_campaign_id(campaign_response)
web_id = get_web_id(campaign_response)
set_content(client, campaign_id, encoded_archive_data)
remove_dir(destination_path)  # Remove destination dir
driver = driver_config(geckodriver_path)  # Configure webdriver
load_website(
    driver,
    username,
    password,
    server_code,
    question1,
    question2,
    question3,
    answer1,
    answer2,
    answer3,
)  # Load Mailchimp site, log in to look over campaign before sending
driver.quit()
