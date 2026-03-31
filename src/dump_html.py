from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

opts = Options()
opts.add_argument("--headless=new")

def smp_html():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.get("https://online.smartmathpro.com/product/m112/")
    time.sleep(5)
    with open("example_detail_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.quit()

def on_demand_html():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.get("https://shoponline.ondemand.in.th/hitpack-dek70.html?")
    time.sleep(5)
    with open("example_ondemand_cat_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    
    driver.get('https://shoponline.ondemand.in.th/20021830cvt.html?')
    time.sleep(5)
    with open("example_ondemand_detail_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.quit()

def we_html():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.get("https://store.webythebrain.com/course/?utm_source=google&utm_medium=cpc&utm_campaign=ads_courses&utm_content=20250111_individualcourses&gad_source=1&gad_campaignid=22112613317&gbraid=0AAAAAprrK5nvznhKnrpaLtAETiL30mGVe&gclid=CjwKCAjwvqjOBhAGEiwAngeQna-QgtYereNoKxejeHddZNiJXOvcg1Mp3IAY7Xul7nPsjQx1GP74hhoCwPQQAvD_BwE")
    time.sleep(5)
    with open("example_we_cat_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.quit()

def we_detail_html():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.get("https://store.webythebrain.com/course/mon94al99/?utm_medium=cpc&utm_source=google&utm_campaign=ads_courses&utm_content=20250111_individualcourses")
    time.sleep(5)
    with open("example_we_detail_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    driver.quit()

if __name__ == "__main__":
    we_detail_html()