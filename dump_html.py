from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

opts = Options()
opts.add_argument("--headless=new")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
driver.get("https://online.smartmathpro.com/product/m112/")
time.sleep(5)
with open("example_detail_page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
driver.quit()
