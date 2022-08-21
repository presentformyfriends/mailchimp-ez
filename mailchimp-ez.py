#!/usr/bin/python3

import os
import shutil
import sys
import pyautogui
import humanize
import logging
import jinja2
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
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from dotenv import load_dotenv

load_dotenv()  # Load environment variables


def check_image_size():
    image_path = Path(sys.argv[1])
    # home_path = Path.home()
    # image_path = (
    #     home_path / "mailchimp-ez/images/"
    # )  # Change from home dir to whatever dir you prefer
    print("Path: " + str(image_path) + "\n")
    input("Press ENTER to continue ...")
    if image_path.is_dir():
        print("\nAdding images from " + str(image_path) + "\n")

        # Check file size of images, reject if any are over 1 MB
        images = []
        file_count = 0
        for file_path in sorted(image_path.glob("*")):
            if file_path.is_file() and (file_path.name).endswith(".jpg"):
                file_count += 1
                image_size = os.stat(file_path).st_size
                if image_size <= 1048576:
                    print("Adding " + str(file_path.name))
                    target = Path(image_path / "image{0}.jpg".format(file_count))
                    file_path.rename(target)                   
                else:
                    natural_image_size = humanize.naturalsize(image_size)
                    print(
                        "Could not add "
                        + file_path.name
                        + " file size too large: "
                        + natural_image_size
                    )
                    print("\nImages must be 1 MB or less\n")
                    sys.exit()
        print("Count:", file_count)

        # Create destination dir, overwrite if it already exists
        campaign_path = home_path / "Documents/campaign"
        try:
            campaign_path.mkdir()
        except FileExistsError:
            shutil.rmtree(campaign_path)
            campaign_path.mkdir()

        # Return source/destination dirs & file count
        print("Image path:", image_path)  # Source dir
        print("Campaign path:", campaign_path)  # Destination dir
        print("File count:", file_count)  # Number of image files
        return image_path, campaign_path, file_count

    elif image_path.is_file():
        print("Invalid selection: path must be directory, not file\n")
        sys.exit()


def copy_images(image_path, campaign_path):
    print("\nCopying files to " + str(campaign_path) + "\n")
    for file in sorted(image_path.glob("*")):
        shutil.copy(file, campaign_path)
        print(str(file) + " copied")


def create_HTML(campaign_path, file_count):
    home_path = Path.home()
    outputfile = home_path / "Documents/campaign/render.html"

    # image1 = "island.jpg"
    # image2 = "guitar.jpg"
    # image3 = "jill.jpg"

    text1 = "Vinyl normcore migas sustainable before they sold out Brooklyn fit air plant whatever salvia vape. Distillery jean shorts banjo helvetica meh umami kale chips asymmetrical shabby chic bicycle rights knausgaard. VHS hexagon JOMO salvia mlkshk, listicle man bun vegan biodiesel. Leggings taxidermy gluten-free glossier biodiesel, green juice ethical kinfolk JOMO slow-carb pinterest."

    text2 = "Glossier neutra cardigan selvage, bitters raclette hammock. Single-origin coffee cloud bread meggings fashion axe master cleanse glossier, austin listicle edison bulb shoreditch. Celiac small batch hell of chia paleo raclette praxis literally tumeric tousled mustache fingerstache pinterest. Jianbing cloud bread gentrify, poke raclette etsy offal sustainable dreamcatcher banh mi humblebrag. Cardigan portland health goth migas, truffaut tousled tote bag sriracha pour-over humblebrag hella praxis YOLO. Roof party sartorial snackwave edison bulb tote bag. Heirloom edison bulb live-edge letterpress."

    text3 = "Four loko air plant whatever gastropub heirloom jianbing. Praxis meditation viral lyft humblebrag, pug butcher irony ennui ramps selvage DSA street art shabby chic. Hella unicorn XOXO sus pitchfork. Thundercats vexillologist tumblr mukbang sus meggings. Heirloom knausgaard succulents gentrify gastropub snackwave sartorial."

    data = [
        [image1, "This is the first image", text1],
        [image2, "This is the second image", text2],
        [image3, "This is the third image", text3],
    ]

    subs = (
        jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
        .get_template("template.html")
        .render(mydata=data)
    )

    # Write substitutions to new file
    with open(outputfile, "w") as f:
        f.write(subs)


def create_archive(campaign_path):
    if "render.html" in os.listdir(campaign_path):
        archive = shutil.make_archive(
            campaign_path, "zip", campaign_path
        )  # args = (base_name, format, root_dir)
        archive_path = Path(archive)
        print("Created " + archive_path.name + "\n")
        return archive_path
    else:
        print("render.html file not found")
        sys.exit()


def encode_archive(archive_path):
    if archive_path.is_file() and str(archive_path).endswith(".zip"):
        try:
            print("Encoding " + archive_path.name + " to utf-8\n")
            with open(archive_path, "rb") as archive:
                return b64encode(archive.read()).decode("utf-8")
        except FileNotFoundError as error:
            print("Encoding of " + archive_path.name + " FAILED")
            sys.exit()
    else:
        print("Invalid archive file")
        sys.exit()


def get_client(api_key, server):
    try:
        client = MailchimpMarketing.Client()
        client.set_config({"api_key": api_key, "server": server})
        return client
    except ApiClientError as error:
        print("Client Error: {}".format(error.text))


def get_health_status(client):
    """
    Check health status
    Response should be: {'health_status': "Everything's Chimpy!"}
    """
    response = client.ping.get()
    print("Response: {}".format(response) + "\n")


def get_response(client, segment_id, list_id, from_name, reply_to_email):
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
                    "subject_line": "Monthly Mailchimp Campaign "
                    + month
                    + " "
                    + year,
                    "title": "Monthly Mailchimp Campaign "
                    + month
                    + " "
                    + year,
                    "from_name": from_name,
                    "reply_to": reply_to_email,
                },
            }
        )
        return campaign_response
    except ApiClientError as error:
        print("Error Creating Campaign: {}".format(error.text))


def get_campaign_id(campaign_response):
    """Grab Campaign ID"""
    try:
        campaign_id = str(campaign_response["id"])
        print("CAMPAIGN ID: " + campaign_id)
        return campaign_id
    except ApiClientError as error:
        print("Campaign ID Error: {}".format(error.text))


def get_web_id(campaign_response):
    """Grab Web ID"""
    try:
        web_id = str(campaign_response["web_id"])
        print("WEB ID: " + web_id)
        return web_id
    except ApiClientError as error:
        print("Web ID Error: {}".format(error.text))


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


def remove_dir(delete_path):
    if os.path.isdir(delete_path):
        shutil.rmtree(delete_path)  # Remove the 'campaign' dir
        print("\nRemoved directory " + str(delete_path) + "\n")
        input("Press ENTER to login to Mailchimp website ...")


def driver_config(geckodriver_path):
    service = Service(geckodriver_path, log_path=os.path.devnull)
    driver = webdriver.Firefox(service=service)
    return driver


def load_website(
    driver,
    username,
    password,
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

    # Login
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//form[@id='login-form']/fieldset/div[@class='line login-field']/div[@class='field-wrapper']/input[@id='username']",
                )
            )
        ).send_keys(username)
    except (NoSuchElementException, TimeoutException) as error:
        print("Couldn't locate username field")

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//form[@id='login-form']/fieldset/div[@id='password-section']/div/input[@id='password']",
                )
            )
        ).send_keys(password)
    except (NoSuchElementException, TimeoutException) as error:
        print("Couldn't locate password field")

    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Log in']"))
        ).click()
    except (NoSuchElementException, TimeoutException) as error:
        print("Couldn't press Log In button")

    # Click radio button
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//label[@class='recover-question']/div/input[@id='dijit_form_RadioButton_1']",
                )
            )
        ).click()  # Try via class name to mitigate TimeoutException
    except (NoSuchElementException, TimeoutException) as error:
        print("Could not click radio button")

    # Answer security question
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#question_answer")
            )
        )
        question = (
            WebDriverWait(driver, 20)
            .until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='radio-description-out question-input fs-mask']/div/p",
                    )
                )
            )
            .text
        )
        answer_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
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
            sys.exit()
    except (NoSuchElementException, TimeoutException) as error:
        print("Could not answer security question")
        sys.exit()

    # Wait for "Submit Verification" button then click it
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[text()=' Submit Verification ']")
            )
        ).click()
    except (NoSuchElementException, TimeoutException) as error:
        print("Could not press Submit Verification button")
        sys.exit()

    # Mitigate for "Updates to our Terms" page
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[text()='Remind me later']")
            )
        ).click()
        print("Skipped Mailchimp update page")
    except (NoSuchElementException, TimeoutException) as error:
        print("No Mailchimp update page detected")

    # Wait for Campaigns link then click it
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//nav/ul/li/button/div/span[text()='Campaigns']")
            )
        ).click()
    except (NoSuchElementException, TimeoutException) as error:
        print("Could not click on Campaigns dropdown")
        sys.exit()

    # Wait for link with current Web ID then click it
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[@aria-label='All campaigns']")
            )
        ).click()
    except (NoSuchElementException, TimeoutException) as error:
        print("Could not click on All Campaigns link")
        sys.exit()


# ENVIRONMENT VARIABLES #

# Credentials
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
api_key = os.environ.get("API_KEY")
server = os.environ.get("SERVER")  # Example: us17
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
geckodriver_path = f"{os.getenv('HOME')}/Downloads/geckodriver"

# From name and reply-to email address
from_name = "Kelly Kapoor"
reply_to_email = "k.kapoor@dundermifflin.com"


# MAIN #

month = datetime.now().strftime("%B")  # Define month
year = datetime.now().strftime("%Y")  # Define year

image_path, campaign_path, file_count = check_image_size()
copy_images(
    image_path, campaign_path
)  # Copy images from user's chosen dir to 'campaign' dir
create_HTML(campaign_path, file_count)  # Render the HTML file
archive_path = create_archive(campaign_path)  # Create archive
encoded_archive_data = encode_archive(archive_path)  # Encode archive to base64
client = get_client(api_key, server)
campaign_response = get_response(
    client, int(segment_id), list_id, from_name, reply_to_email
)
campaign_id = get_campaign_id(campaign_response)
web_id = get_web_id(campaign_response)
set_content(client, campaign_id, encoded_archive_data)
remove_dir(campaign_path)  # Remove 'campaign' dir
driver = driver_config(geckodriver_path)
load_website(
    driver,
    username,
    password,
    question1,
    question2,
    question3,
    answer1,
    answer2,
    answer3,
)  # Load Mailchimp site, log in to look over campaign before sending
