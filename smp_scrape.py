import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- ข้อมูล Input: รายการ URL หมวดหมู่ ---
category_urls = [
    "https://online.smartmathpro.com/product-c/smartmathpro/dek70/",
    "https://online.smartmathpro.com/product-c/smartmathpro/m6/",
    "https://online.smartmathpro.com/product-c/smartmathpro/m5/",
    "https://online.smartmathpro.com/product-c/smartmathpro/m4/",
    "https://online.smartmathpro.com/product-c/smartmathpro/buffet/",
    "https://online.smartmathpro.com/product-c/smartmathpro/m456-pack/",
    "https://online.smartmathpro.com/product-c/smartmathpro/m456-chapter/",
    "https://online.smartmathpro.com/product-c/smartmathpro/tgat-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/tpat1-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/tpat3-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/tpat5-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/alevelmath1-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/alevelmath2-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/alevelphy-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/alevelbio-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/aleveleng-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/alevelth-soc-a/",
    "https://online.smartmathpro.com/product-c/smartmathpro/basic/",
    "https://online.smartmathpro.com/product-c/smartmathpro/uni/",
    "https://online.smartmathpro.com/product-c/smartmathpro/comart/",
    "https://online.smartmathpro.com/product-c/smartmathpro/comart/", # ตัวซ้ำ
    "https://online.smartmathpro.com/product-c/smartmathpro/edu/"
]

# --- 0. Deduplication (จัดการ URL หมวดหมู่ที่ซ้ำ) ---
category_urls = list(dict.fromkeys(category_urls))

# ฟังก์ชันจัดหมวดหมู่ตามชื่อคอร์ส
def categorize_subject(name):
    name = name.lower()
    if 'math' in name or 'คณิต' in name: return 'คณิตศาสตร์'
    if 'phy' in name or 'ฟิสิกส์' in name: return 'ฟิสิกส์'
    if 'bio' in name or 'ชีวะ' in name: return 'ชีววิทยา'
    if 'eng' in name or 'อังกฤษ' in name: return 'ภาษาอังกฤษ'
    if 'เคมี' in name: return 'เคมี'
    if 'tpat' in name or 'tgat' in name: return 'ความถนัด/TGAT/TPAT'
    return 'อื่นๆ'

def categorize_type(name):
    name = name.lower()
    if 'alevel' in name or 'ติวสอบ' in name: return 'ติวสอบ A-Level'
    if 'pack' in name or 'บุฟเฟต์' in name or 'buffet' in name: return 'คอร์สแพ็กเกจ'
    if 'ปูพื้นฐาน' in name or 'basic' in name: return 'ปูพื้นฐาน'
    return 'ติวเนื้อหา/เสริมเกรด'

# ตั้งค่า Selenium
chrome_options = Options()
# chrome_options.add_argument("--headless") # เปิดใช้งานหากต้องการรันเบื้องหลัง
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 10)

all_course_links = set() # ป้องกันคอร์สซ้ำข้ามหมวดหมู่

try:
    # --- STEP 1: กวาด URL คอร์สทั้งหมดจากหน้ารวม ---
    print("--- Step 1: Collecting Course Links ---")
    for cat_url in category_urls:
        print(f"กำลังเปิดหมวดหมู่: {cat_url}")
        try:
            driver.get(cat_url)
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.woocommerce-LoopProduct-link")))
            course_elements = driver.find_elements(By.CSS_SELECTOR, "a.woocommerce-LoopProduct-link")
            for elem in course_elements:
                link = elem.get_attribute("href")
                if link:
                    all_course_links.add(link)
        except Exception as e:
            print(f"ข้ามหมวดหมู่ {cat_url} เนื่องจาก Error: {e}")

    course_list = list(all_course_links)
    print(f"พบคอร์สเรียนทั้งหมด (Unique): {len(course_list)} คอร์ส")

    # --- STEP 2: วนลูปเข้าไปเก็บข้อมูลในหน้ารายละเอียด ---
    print("\n--- Step 2: Scraping Course Details ---")
    results = []

    for index, course_url in enumerate(course_list, 1):
        print(f"({index}/{len(course_list)}) กำลังดึงข้อมูล: {course_url}")
        try:
            driver.get(course_url)
            time.sleep(1) # รอให้ Render ข้อมูล
            
            # ดึงชื่อคอร์สก่อนเพื่อใช้จัดหมวดหมู่
            try:
                name = driver.find_element(By.CSS_SELECTOR, "h1.product_title").text.strip()
            except: name = "N/A"

            row = {
                "institute_name": "SmartMathPro",
                "course_name": name,
                "subject": categorize_subject(name),
                "course_type": categorize_type(name),
                "learning_format": "วิดีโอ (ออนไลน์)",
                "total_hours": 0.0,
                "price": 0.0,
                "price_per_hour": 0.0,
                "url": course_url
            }

            # 1. ดึงราคา (Price)
            try:
                price_elem = driver.find_elements(By.CSS_SELECTOR, "p.price ins bdi, p.price bdi")
                if price_elem:
                    price_val = re.sub(r'[^\d.]', '', price_elem[0].text)
                    row["price"] = float(price_val) if price_val else 0.0
            except: pass

            # 2. ดึงจำนวนชั่วโมง (Total Hours)
            try:
                duration_text = driver.find_element(By.CSS_SELECTOR, ".sec-time p").text
                # ดึงตัวเลขจากข้อความ เช่น "230 ชั่วโมง"
                hours_match = re.findall(r'[\d.]+', duration_text)
                if hours_match:
                    row["total_hours"] = float(hours_match[0])
            except: pass

            # 3. คำนวณราคาต่อชั่วโมง (Price per Hour)
            if row["price"] > 0 and row["total_hours"] > 0:
                row["price_per_hour"] = round(row["price"] / row["total_hours"], 2)

            results.append(row)
        except Exception as e:
            print(f"Error scraping {course_url}: {e}")

    # --- Export: บันทึกข้อมูลเป็น CSV ---
    df = pd.DataFrame(results)
    df.to_csv("smartmathpro_raw.csv", index=False, encoding='utf-8-sig')
    print("\nScraping เสร็จสมบูรณ์! บันทึกข้อมูลลงไฟล์ 'smartmathpro_raw.csv' เรียบร้อยแล้ว")

finally:
    driver.quit()
