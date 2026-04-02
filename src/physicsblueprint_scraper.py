import pandas as pd
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Input: Physics Blueprint Category URLs ---
category_urls = [
    'https://www.physicsblueprint.com/course-promotion/',
    'https://www.physicsblueprint.com/course-speedup/',
    'https://www.physicsblueprint.com/course-tpat3/',
    'https://www.physicsblueprint.com/course-physicsentrance/',
    'https://www.physicsblueprint.com/course-physicshs/',
    'https://www.physicsblueprint.com/course-chapters/',
    'https://www.physicsblueprint.com/course-tgat/'
]

def categorize_subject(name):
    name = name.lower()
    subjects = []
    if 'math' in name or 'คณิต' in name: subjects.append('คณิตศาสตร์')
    if 'phy' in name or 'ฟิสิกส์' in name: subjects.append('ฟิสิกส์')
    if 'tpat3' in name or 'ความถนัดวิศวะ' in name: subjects.append('ฟิสิกส์/ความถนัดวิศวะ')
    if 'tgat' in name: subjects.append('ความถนัด/TGAT')
    if len(subjects) > 1: return 'Mixed'
    if len(subjects) == 1: return subjects[0]
    return 'ฟิสิกส์'

def categorize_type(name):
    name = name.lower()
    if 'alevel' in name or 'ติวสอบ' in name or 'tcas' in name or 'a-level' in name or 'entrance' in name: return 'ติวสอบ A-Level/TCAS'
    if 'pack' in name or 'แพ็ก' in name or 'แพ็ค' in name: return 'คอร์สแพ็กเกจ'
    if 'ม.4' in name or 'ม.5' in name or 'ม.6' in name: return 'ติวเนื้อหา/เสริมเกรด'
    if 'สอวน' in name or 'olympic' in name: return 'สอบเข้า ม.4 / โอลิมปิก'
    return 'ติวเนื้อหา/เสริมเกรด'

# Setup Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

all_course_links = set()

try:
    print("--- Step 1: Collecting Course Links from Physics Blueprint ---")
    for cat_url in category_urls:
        print(f"\nกำลังเปิดหมวดหมู่: {cat_url}")
        try:
            driver.get(cat_url)
            time.sleep(3) # รอให้เว็บโหลดส่วนแรกเสร็จ
            
            print("  [>] กำลังไถหน้าจอเพื่อโหลดคอร์สที่ซ่อนอยู่ (Lazy Loading)...")
            # --- ระบบไถหน้าจอลงไปล่างสุด ---
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # สั่งเลื่อนจอลงไปล่างสุด
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) # รอให้รูปและข้อมูลคอร์สใหม่เด้งขึ้นมา
                
                # เช็คว่าความสูงเว็บเพิ่มขึ้นไหม (ถ้าไม่เพิ่มแปลว่าสุดหน้าแล้ว)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # --- เริ่มกวาดลิงก์หลังจากเว็บโหลดข้อมูลครบหมดแล้ว ---
            product_links = driver.find_elements(By.CSS_SELECTOR, "a.woocommerce-LoopProduct-link")
            links_added = 0
            
            for link_elem in product_links:
                if link_elem.is_displayed(): # เพิ่มการเช็คว่าคอร์สนั้นแสดงบนหน้าเว็บจริงๆ (กันพวก hidden/mobile view)
                    url = link_elem.get_attribute("href")
                    if url and url not in all_course_links:
                        all_course_links.add(url)
                        links_added += 1
                    
            print(f"  [+] เก็บลิงก์สำเร็จ {links_added} คอร์ส")

        except Exception as e:
            print(f"  [-] Error ในหน้า {cat_url}: {e}")

    course_list = list(all_course_links)
    print(f"\nสรุป Step 1: พบคอร์สเรียนทั้งหมด (Unique): {len(course_list)} คอร์ส")

    print("\n--- Step 2: Scraping Course Details ---")
    results = []

    for index, course_url in enumerate(course_list, 1):
        # if index > 5: break 
        print(f"({index}/{len(course_list)}) Scraping: {course_url}")
        try:
            driver.get(course_url)
            time.sleep(3) # Wait for content
            
            # Name
            name = "N/A"
            name_selectors = ["h1.product_title", "h1.course_title", "title"]
            for sel in name_selectors:
                try:
                    if sel == "title":
                        name = driver.title.split('-')[0].strip()
                    else:
                        name = driver.find_element(By.CSS_SELECTOR, sel).get_attribute("textContent").strip()
                    if name and name != "N/A": break
                except: continue
            
            # Price
            price_val = 0.0
            price_selectors = [".price ins .amount", ".price .amount", "p.price .amount"]
            for sel in price_selectors:
                try:
                    price_text = driver.find_element(By.CSS_SELECTOR, sel).get_attribute("textContent").strip()
                    val_str = re.sub(r'[^\d.]', '', price_text)
                    if val_str:
                        price_val = float(val_str)
                        break
                except: continue
            
            # Tutor
            tutor = "ครูพี่ตั้ว"
            
            # Total Hours
            total_hours = 0.0
            try:
                # 1. Try "ชั่วโมงคอร์ส" in icon-details-item
                try:
                    hour_h3 = driver.find_element(By.XPATH, "//h3[contains(text(), 'ชั่วโมงคอร์ส')]")
                    hour_p = hour_h3.find_element(By.XPATH, "./following-sibling::p")
                    hour_text = hour_p.get_attribute("textContent").strip()
                    match = re.search(r'([\d,.]+)', hour_text)
                    if match:
                        total_hours = float(match.group(1).replace(',', ''))
                except: pass
                
                # 2. Try common clock icon sibling
                if total_hours == 0:
                    try:
                        clock_elem = driver.find_element(By.CSS_SELECTOR, ".fa-clock, img[src*='clock']")
                        parent = clock_elem.find_element(By.XPATH, "./..")
                        text = parent.get_attribute("textContent").strip()
                        match = re.search(r'([\d,.]+)\s*(ชั่วโมง|hours|ชม)', text)
                        if match:
                            total_hours = float(match.group(1).replace(',', ''))
                    except: pass
                
                # 3. Fallback search entire body
                if total_hours == 0:
                    body_text = driver.find_element(By.TAG_NAME, "body").get_attribute("textContent")
                    # Try specific "ชั่วโมงคอร์ส X ชั่วโมง" pattern first
                    match = re.search(r'ชั่วโมงคอร์ส\s*([\d,.]+)\s*ชั่วโมง', body_text)
                    if match:
                        total_hours = float(match.group(1).replace(',', ''))
                    else:
                        match = re.search(r'([\d,.]+)\s*(ชั่วโมง|hours|ชม)', body_text)
                        if match:
                            total_hours = float(match.group(1).replace(',', ''))
            except: pass

            price_per_hour = price_val / total_hours if total_hours > 0 else 0.0

            row = {
                "institute_name": "Physics Blueprint",
                "course_name": name,
                "tutor": tutor,
                "subject": categorize_subject(name),
                "course_type": categorize_type(name),
                "learning_format": "วิดีโอออนไลน์",
                "total_hours": round(total_hours, 2),
                "price": price_val,
                "price_per_hour": round(price_per_hour, 2),
                "url": course_url
            }
            results.append(row)
            
        except Exception as e:
            print(f"Error scraping {course_url}: {e}")

    # Save to CSV
    if results:
        df = pd.DataFrame(results)
        output_file = "data/physicsblueprint_courses.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\nSaved {len(results)} courses to {output_file}")
    else:
        print("\nNo data collected.")

finally:
    driver.quit()
