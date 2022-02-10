from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd

# Credentials (You must be linked with amazon affiliate program)
email = "Your Email"
password = "Your password"

# Dictionary to store our data
skinCareProducts = {}
no_of_products = 1

# Executing Driver ,
ser = Service("C:\chromedriver.exe")  # Set your own driver path
op = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=ser, options=op)

# Signing in
url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
driver.get(url)
email_box = driver.find_element(By.ID, "ap_email")
email_box.send_keys(email)
email_box.send_keys(Keys.ENTER)
sleep(3)
password_box = driver.find_element(By.ID, "ap_password")
password_box.send_keys(password)
password_box.send_keys(Keys.ENTER)
sleep(30)
# Signing Complete

# This img_count will be the name of your images
img_count = 1

# Search url of skin care products
driver.get(
    'https://www.amazon.com/s?k=skin+care+products&dc&crid=2KCTH7IZY54S0&sprefix=skincare+product%2Caps%2C520&ref=a9_sc_1')
sleep(3)
prices = []
names = []
aff_links = []
data = driver.page_source
soup = bs(data, 'html.parser')
listing = soup.find('div', {'class': "s-main-slot s-result-list s-search-results sg-row"})
products = listing.find_all('div', {"data-component-type": 's-search-result'})
print(len(products))
for product in products:
    if product.find('span', {"class": "a-price-whole"}):  # only want products with prices
        # using try and except for skiping unwanted products
        try:
            name = product.find('span', {"class": "a-size-base-plus a-color-base a-text-normal"}).text.strip()
            print(name)
            price = product.find('span', {'class': "a-price-whole"}).text.strip()
            image_src = product.find('img', {'class': "s-image"}).get('src')
            response = requests.get(image_src)
            #  Storing images
            with open(f"images\{img_count}.png", "wb") as file:
                file.write(response.content)
            img_count += 1
            product_url = "https://www.amazon.com" + product.find('a', {
                "class": "a-link-normal s-link-style a-text-normal"}).get('href')
            print(product_url)
            driver.get(product_url)
            sleep(5)
            driver.find_element(By.LINK_TEXT, "Text").click()
            sleep(5)
            data = driver.page_source
            soup = bs(data, 'html.parser')
            aff_link = soup.find('textarea', {'id': "amzn-ss-text-shortlink-textarea"}).text.strip()
            print(name, "\n", price, "\n", aff_link)
            # Checking if the affiliate link is valid
            if "https" in aff_link:
                skinCareProducts[no_of_products] = [name, price, aff_link]
                no_of_products += 1
                print("Added")
            else:
                print("Could'nt found affiliate")
        except:
            print("<--------Out of track----------->")
            pass
    else:
        print("<--------Skipped product because out of stock----------->")
        pass

# Creating a dataframe with pandas from dictionary
df = pd.DataFrame.from_dict(skinCareProducts, orient="index", columns=["name", "price", "affiliate link"])

# Output in Csv
df.to_csv("SkinProducts.csv")
