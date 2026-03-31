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

# --- ข้อมูล Input: รายการ URL หมวดหมู่ (Category Pages) ---
category_urls = [
    "https://shoponline.ondemand.in.th/hitpack-dek70.html",
    "https://shoponline.ondemand.in.th/dek70-tcas-upskill.html",
    "https://shoponline.ondemand.in.th/dek70-tcas-5.html",
    "https://shoponline.ondemand.in.th/med-for-dek-70.html",
    "https://shoponline.ondemand.in.th/tcasdek69.html",
    "https://shoponline.ondemand.in.th/dek69-tcas.html",
    "https://shoponline.ondemand.in.th/senior-high-school/2pack-course-may.html",
]

# กำจัด URL ซ้ำ
category_urls = list(dict.fromkeys(category_urls))

# ฟังก์ชันจัดหมวดหมู่วิชา
def categorize_subject(name):
    name = name.lower()
    if 'math' in name or 'คณิต' in name: return 'คณิตศาสตร์'
    if 'phy' in name or 'ฟิสิกส์' in name: return 'ฟิสิกส์'
    if 'bio' in name or 'ชีวะ' in name: return 'ชีววิทยา'
    if 'eng' in name or 'อังกฤษ' in name: return 'ภาษาอังกฤษ'
    if 'เคมี' in name: return 'เคมี'
    if 'tpat' in name or 'tgat' in name: return 'ความถนัด/TGAT/TPAT'
    return 'อื่นๆ'

# ฟังก์ชันจัดประเภทคอร์ส
def categorize_type(name):
    name = name.lower()
    if 'alevel' in name or 'ติวสอบ' in name or 'tcas' in name: return 'ติวสอบ A-Level/TCAS'
    if 'pack' in name or 'แพ็ก' in name: return 'คอร์สแพ็กเกจ'
    if 'ปูพื้นฐาน' in name or 'basic' in name: return 'ปูพื้นฐาน'
    return 'ติวเนื้อหา/เสริมเกรด'

# ตั้งค่า Selenium
chrome_options = Options()
# chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

all_course_links = set()

try:
    # --- STEP 1: กวาด URL ของ Detail Page จากหน้า Category ---
    print("--- Step 1: Collecting Detail Page Links from Category Pages ---")
    for cat_url in category_urls:
        print(f"กำลังเปิดหน้าหมวดหมู่: {cat_url}")
        try:
            driver.get(cat_url)
            
            # ใช้ WebDriverWait รอจนกว่ากล่องคอร์ส (catalog-card) จะโผล่ขึ้นมาบนหน้าเว็บ
            # เพื่อแก้ปัญหาหน้าเว็บโหลดช้าแล้ว Selenium ดึงข้อมูลไม่ทัน
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.catalog-card")))
            time.sleep(1) # เผื่อเวลาให้ JS render ลิงก์เสร็จอีกนิด
            
            # ยิง CSS Selector ไปที่ <a> ที่มีคลาส product-item-photo ซึ่งอยู่ใต้ div.catalog-card
            course_elements = driver.find_elements(By.CSS_SELECTOR, "div.catalog-card a.product-item-photo")
            
            current_cat_links = 0
            for elem in course_elements:
                link = elem.get_attribute("href")
                
                if link and ".html" in link:
                    # ตัด query string ? ออก (โค้ดส่วนนี้ของคุณเขียนไว้ดีมากครับ)
                    clean_link = link.split('?')[0]
                    if clean_link not in all_course_links:
                        all_course_links.add(clean_link)
                        current_cat_links += 1
            
            print(f"พบลิงก์คอร์สเรียนใหม่: {current_cat_links} ลิงก์")
            
        except Exception as e:
            print(f"ข้ามหน้าหมวดหมู่ {cat_url} เนื่องจากไม่มีคอร์ส หรือ Error: {e}")

    course_list = list(all_course_links)
    print(f"\nสรุป: พบคอร์สเรียนทั้งหมด (Unique): {len(course_list)} คอร์ส")

    # --- STEP 2: เข้าไปในแต่ละ Detail Page เพื่อดึงข้อมูล ---
    print("\n--- Step 2: Scraping Data from each Detail Page ---")
    results = []

    for index, course_url in enumerate(course_list, 1):
        print(f"({index}/{len(course_list)}) กำลังดึงข้อมูล: {course_url}")
        try:
            driver.get(course_url)
            time.sleep(2) # รอให้หน้าโหลดเสร็จ
            
            # 1. ชื่อคอร์ส
            try:
                name_elem = driver.find_element(By.CSS_SELECTOR, "div.box-tags h4")
                name = name_elem.text.strip()
            except:
                try:
                    name = driver.find_element(By.CSS_SELECTOR, "h1.page-title").text.strip()
                except:
                    name = "N/A"
            
            # 2. ราคา
            try:
                # ลองดึงราคาลด (Final Price) ก่อน
                price_elem = driver.find_element(By.CSS_SELECTOR, "span.price-wrapper[data-price-type='finalPrice'] span.price")
                price_text = price_elem.text.strip()
            except:
                try:
                    price_text = driver.find_element(By.CSS_SELECTOR, "span.price").text.strip()
                except:
                    price_text = "0"
            
            price_val = float(re.sub(r'[^\d.]', '', price_text)) if re.sub(r'[^\d.]', '', price_text) else 0.0
            
            # 3. ติวเตอร์ (ครูผู้สอน)
            tutor = "N/A"
            try:
                detail_block = driver.find_element(By.CSS_SELECTOR, "div.product-detail-block")
                detail_text = detail_block.text
                teacher_match = re.search(r'ครูผู้สอน:\s*(.*)', detail_text)
                if teacher_match:
                    tutor = teacher_match.group(1).strip()
            except:
                pass
            
            # 4. จำนวนชั่วโมงเรียน
            total_hours = 0.0
            try:
                # ใช้ XPath หา <span> ที่มีคำว่า 'ความยาว' 
                # จากนั้นเลือก <span> ตัวถัดไป (following-sibling) ที่เก็บตัวเลขไว้
                hour_elem = driver.find_element(By.XPATH, "//span[contains(text(), 'ความยาว')]/following-sibling::span")
                hour_text = hour_elem.text.strip() # จะได้ข้อความเช่น "247 ชม."
                
                # ใช้ Regex ดึงเฉพาะตัวเลขและจุดทศนิยม
                hour_match = re.search(r'([\d.]+)', hour_text)
                if hour_match:
                    total_hours = float(hour_match.group(1))
            except:
                pass

            # คำนวณราคาต่อชั่วโมง
            price_per_hour = price_val / total_hours if total_hours > 0 else 0.0

            # 5. สร้าง Dictionary ตามรูปแบบที่ต้องการ
            row = {
                "institute_name": "OnDemand",
                "course_name": name,
                "tutor": tutor,
                "subject": categorize_subject(name),
                "course_type": categorize_type(name),
                "learning_format": "วิดีโอ (ออนไลน์/สาขา)",
                "total_hours": total_hours,
                "price": price_val,
                "price_per_hour": round(price_per_hour, 2),
                "url": course_url
            }
            results.append(row)
            
        except Exception as e:
            print(f"Error ในหน้า {course_url}: {e}")

    # --- STEP 3: บันทึกผลลง CSV ---
    if results:
        df = pd.DataFrame(results)
        # เปลี่ยนชื่อไฟล์ให้เซฟไว้ที่เดียวกับโค้ดเลย จะได้หาง่ายๆ
        output_path = "ondemand_courses.csv" 
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\nเสร็จสิ้น! บันทึกข้อมูล {len(results)} คอร์ส ลงในไฟล์ {output_path}")
    else:
        print("\nไม่สามารถดึงข้อมูลได้ (ไม่มีข้อมูลใน results เลย)")

finally:
    driver.quit()
