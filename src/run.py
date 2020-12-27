from selenium import webdriver
from email.message import EmailMessage
import time
import smtplib
import threading
import datetime
import pytz
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options

# home shortcut command left and right
# switch different instances of an app. command + tilda
# page up and down. fn + up and down
# sudo chmod 777

# take in a list of linksc
# Docker!
# Make classes

# find ~/.virtualenvs/my-virtual-env/ -type l -delete
# virtualenv ~/.virtualenvs/my-virtual-env
# virtualenv -p python3 <desired-path>

emailaddress = "emailaddress"
emailpassword = "emailpassword"

def sendmail(content):
    msg = EmailMessage()
    msg['From'] = emailaddress
    msg['To'] = emailaddress
    msg.set_content(content)
    msg['Subject'] = content

    s = smtplib.SMTP("smtp.live.com", 587)
    s.ehlo()  # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls()  # Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(emailaddress, emailpassword)

    s.sendmail(emailaddress, emailaddress, msg.as_string())

    s.quit()

def isSingleInStock(driver):
    isInStock = False

    inStockTargets = driver.find_elements_by_xpath("//div[@class='product-inventory']")

    for inStockText in inStockTargets:
        cleanText = inStockText.text.strip().lower()
        if cleanText == "":
            continue

        if "in stock" in cleanText:
            isInStock = True

        if "out of stock" not in cleanText:
            isInStock = True

    return isInStock


def isComboInStock(driver):
    isInStock = False

    inStockTargets = driver.find_elements_by_xpath("//p[@class='note']")

    for inStockText in inStockTargets:
        cleanText = inStockText.text.strip().lower()
        if cleanText == "":
            continue

        if "out of stock" not in cleanText:
            isInStock = True

    return isInStock

def microcenter_is_in_stock(driver):
    isInStock = False

    inStockTargets = driver.find_elements_by_xpath("//p[@class='inventory']")

    for inStockText in inStockTargets:
        cleanText = inStockText.text.strip().lower()

        if cleanText == "":
            continue

        if "sold out" not in cleanText:
            isInStock = False

    return isInStock

def isInStock(driver, url):
    if 'newegg.com' in url.lower():
        if 'combo' in url.lower():
            return isComboInStock(driver)
        else:
            return isSingleInStock(driver)
    elif 'microcenter.com' in url.lower():
        return microcenter_is_in_stock(driver)

    return False

def utc_to_local(utc_dt):
    local_tz = pytz.timezone('US/Eastern')
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def wait_until_visible(driver, xpath):

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))

def wait_and_click(driver, xpath):
    wait_until_visible(driver, xpath)
    driver.find_element_by_xpath(xpath).click()

def wait_and_send(driver, xpath, text):
    wait_until_visible(driver, xpath)
    driver.find_element_by_xpath(xpath).send_keys(text)

newegg_username = "yourusername"
newegg_password = "yourpasswordls"

def login(driver):

    driver.get("https://www.newegg.com/")

    wait_and_click(driver, "//div[text()='Sign in / Register']")
    wait_and_send(driver, "//input[@id='labeled-input-signEmail']", newegg_username)
    wait_and_click(driver, "//button[@id='signInSubmit']")

    wait_and_send(driver, "//input[@id='labeled-input-password']", newegg_password)
    wait_and_click(driver, "//button[@id='signInSubmit']")


def runthread(url):

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    #driver = webdriver.Remote(
    #    command_executor='http://localhost:4444/wd/hub',
    #    desired_capabilities={'browserName': 'chrome', 'javascriptEnabled': True},
    #    options=chrome_options)

    chrome_path = r'/usr/local/bin/chromedriver'
    driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)

    #login(driver)

    driver.get(url)

    while not isInStock(driver, url):
        driver.refresh()
        time.sleep(2)

    print("In Stock!" + utc_to_local(datetime.datetime.utcnow()).strftime("%m/%d/%Y %H:%M:%S") + " " + url)

    sendmail(url)

class link:

    def __init__(self, url, isCombo):
        self.url = url
        self.isCombo = isCombo


def main():
    thread_list = list()

    urls = []

    urls.append("https://www.newegg.com/msi-geforce-rtx-3070-rtx-3070-gaming-x-trio/p/N82E16814137603?Description=3070%20trio&cm_re=3070_trio-_-14-137-603-_-Product")
    urls.append("https://www.newegg.com/asus-geforce-rtx-3070-tuf-rtx3070-o8g-gaming/p/N82E16814126461?Description=asus%20tuf%203070&cm_re=asus_tuf%203070-_-14-126-461-_-Product")
    urls.append("https://www.newegg.com/Product/ComboDealDetails?ItemList=Combo.4210714&quicklink=true")
    index = 1

    # Start test
    for url in urls:
        t = threading.Thread(name='Test {}'.format(index), target=runthread, args=(url,))
        t.start()
        time.sleep(1)
        print(t.name + ' started!')
        thread_list.append(t)
        index = index + 1

    # Wait for all threads to complete
    for thread in thread_list:
        thread.join()

    print('Program completed!')

main()