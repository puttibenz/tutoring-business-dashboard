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

# --- Input: Panya Society Catalog URL ---
PANYA_URL = "https://panyasociety.com/course/list"

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
    if 'alevel' in name or 'tcas' in name: return 'ติวสอบ A-Level/TCAS'
    if 'pack' in name: return 'คอร์สแพ็กเกจ'
    if 'พื้นฐาน' in name: return 'ปูพื้นฐาน'
    return 'ติวเนื้อหา/เสริมเกรด'

# ตั้งค่า Selenium
chrome_options = Options()
# chrome_options.add_argument("--headless=new") # แนะนำให้เปิดจอไว้ดูก่อนว่าบอทเลื่อนจอสำเร็จไหม
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

all_course_links = set()

# ฟังก์ชันพิเศษสำหรับเคลียร์ Pop-up และ Cookie Banner
# ฟังก์ชันพิเศษสำหรับเคลียร์ Pop-up (SweetAlert2) และ Cookie Banner
def clear_popups(driver):
    print("    [!] กำลังสแกนหา Pop-up และคุกกี้...")
    
    # 1. จัดการ Pop-up โฆษณาตรงกลางจอ (SweetAlert2)
    try:
        # ล็อกเป้าไปที่ปุ่มที่มีคลาส swal2-confirm (จากในรูปที่คุณแคปมา)
        # ให้เวลามันเด้งขึ้นมาสูงสุด 5 วินาที
        popup_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.swal2-confirm"))
        )
        # ใช้ JS ยิงคำสั่งคลิก
        driver.execute_script("arguments[0].click();", popup_btn)
        print("    [+] ปิด Pop-up โฆษณาสำเร็จ!")
        time.sleep(1) # รอให้แอนิเมชัน Pop-up หายไปจากจอ
    except Exception:
        pass # ถ้าไม่เจอ (บางทีเปิดรอบสองมันไม่เด้งแล้ว) ก็ปล่อยผ่านไป
        
    # 2. จัดการแถบคุกกี้ด้านล่าง ("ยินยอม")
    try:
        # หาปุ่มที่มีคำว่า ยินยอม
        cookie_btns = driver.find_elements(By.XPATH, "//button[contains(text(), 'ยินยอม')]")
        for btn in cookie_btns:
            driver.execute_script("arguments[0].click();", btn)
            print("    [+] ปิดแถบคุกกี้สำเร็จ!")
    except Exception:
        pass

try:# --- STEP 1: กวาด URL แบบ Infinite Scroll ---
    print("--- Step 1: Collecting Panya Society Course Links ---")
    driver.get(PANYA_URL)
    time.sleep(3) 
    
    # ฆ่า Pop-up ก่อนเริ่มงาน (อย่าลืมเอาฟังก์ชัน clear_popups ไปวางไว้ด้านบนโค้ดด้วยนะครับ)
    clear_popups(driver) 
    
    print("กำลังเริ่มไถหน้าจอเพื่อโหลดคอร์สให้ครบ...")
    
    last_count = 0
    retries = 0
    
    # ลูปไถจอแบบค่อยๆ เลื่อน
    while True:
        # หาการ์ดคอร์สทั้งหมดที่มีบนหน้าจอ ณ ตอนนั้น
        cards = driver.find_elements(By.CSS_SELECTOR, "div.course-card")
        current_count = len(cards)
        print(f"  [+] โหลดมาแล้ว {current_count} คอร์ส...")
        
        # ถ้ายอดโหลดถึง 75 แล้ว (ตามที่คุณเห็นบนเว็บ) ให้หยุดไถจอได้เลย
        if current_count >= 75:
            print("  [!] โหลดคอร์สครบ 75 รายการตามเป้าหมายแล้ว!")
            break
            
        # ถ้ายอดคอร์สไม่เพิ่มขึ้นเลย
        if current_count == last_count:
            retries += 1
            if retries >= 3: # ให้โอกาสเว็บโหลด 3 รอบ ถ้าไม่มาแปลว่าสุดทางแล้ว
                print("  [!] สุดหน้าเว็บแล้ว ไม่มีการโหลดข้อมูลเพิ่ม")
                break
        else:
            retries = 0 # รีเซ็ตจำนวนรอบถ้ายอดคอร์สเพิ่มขึ้น
            
        last_count = current_count
        
        # จุดสำคัญ: สั่งให้เมาส์เลื่อนไปโฟกัสที่ "คอร์สตัวสุดท้าย" ที่เพิ่งโหลดมา
        if cards:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cards[-1])
        time.sleep(2) # รอเวลาให้เซิร์ฟเวอร์ Panya ส่งข้อมูลชุดใหม่มา

    print("กำลังแยกแยะลิงก์คอร์สเรียน...")
    # กวาดลิงก์จากคอร์สทั้งหมดที่โหลดมาได้
    course_elements = driver.find_elements(By.CSS_SELECTOR, "div.course-card a[href*='/course/preview/']")
    for elem in course_elements:
        link = elem.get_attribute("href")
        if link:
            clean_link = link.split('?')[0]
            all_course_links.add(clean_link)
            
    course_list = list(all_course_links)
    print(f"\nสรุป Step 1: พบคอร์สเรียนทั้งหมด (Unique): {len(course_list)} คอร์ส")

    # --- STEP 2: เข้าไปเก็บข้อมูลในหน้ารายละเอียด ---
    print("\n--- Step 2: Scraping Details ---")
    results = []

    for index, course_url in enumerate(course_list, 1):
        print(f"({index}/{len(course_list)}) กำลังดึงข้อมูล: {course_url}")
        try:
            driver.get(course_url)
            
            # ใช้ WebDriverWait รอให้ชื่อคอร์สโหลดเสร็จ (รอคลาส .bold-text-8)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".bold-text-8")))
            time.sleep(1) # เผื่อเวลาให้ render ส่วนอื่นๆ
            
            row = {
                "institute_name": "Panya Society",
                "course_name": "N/A",
                "tutor": "N/A",
                "subject": "อื่นๆ",
                "course_type": "ติวเนื้อหา/เสริมเกรด",
                "learning_format": "วิดีโอ (ออนไลน์)",
                "total_hours": 0.0,
                "price": 0.0,
                "price_per_hour": 0.0,
                "url": course_url
            }
            
            # 1. ดึงชื่อคอร์ส (จากคลาส bold-text-8)
            try:
                name_elem = driver.find_element(By.CSS_SELECTOR, ".bold-text-8")
                row["course_name"] = name_elem.text.strip()
                row["subject"] = categorize_subject(row["course_name"])
                row["course_type"] = categorize_type(row["course_name"])
            except: pass
            
            # 2. ดึงติวเตอร์ (กวาดทุกคนที่อยู่ในคลาส text-block-101)
            try:
                tutor_elems = driver.find_elements(By.CSS_SELECTOR, ".text-block-101")
                if tutor_elems:
                    row["tutor"] = ", ".join([t.text.strip() for t in tutor_elems if t.text.strip() != ""])
            except: pass

            # 3. ดึงจำนวนชั่วโมง (จากคลาส text-block-20)
            try:
                hour_elem = driver.find_element(By.CSS_SELECTOR, ".text-block-20")
                hour_text = hour_elem.text.strip() # เช่น "1213 lectures • 308 hours"
                
                # ใช้ Regex ดักจับตัวเลขที่อยู่หน้าคำว่า hours
                hour_match = re.search(r'([\d.]+)\s*hours', hour_text, re.IGNORECASE)
                if hour_match:
                    row["total_hours"] = float(hour_match.group(1))
            except: pass

            # 4. ดึงราคา (ยังคงใช้ Regex กวาดจากหน้าเว็บ เพราะในรูปไม่ได้แคปส่วนราคามาให้)
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                price_matches = re.findall(r'฿([\d,]+)', page_text)
                if price_matches:
                    price_str = price_matches[-1].replace(',', '')
                    row["price"] = float(price_str)
            except: pass
            
            # 5. คำนวณราคาต่อชั่วโมง
            if row["price"] > 0 and row["total_hours"] > 0:
                row["price_per_hour"] = round(row["price"] / row["total_hours"], 2)
                
            results.append(row)
            
        except Exception as e:
            print(f"Error scraping {course_url}: {e}")

    # --- STEP 3: Save to CSV ---
    if results:
        df = pd.DataFrame(results)
        output_file = "panya_courses.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n🎉 สำเร็จ! บันทึกข้อมูล {len(results)} คอร์ส ลงใน {output_file} เรียบร้อยแล้ว")
    else:
        print("\nไม่มีข้อมูลถูกบันทึกเลย ลองตรวจสอบ HTML Selector อีกครั้งครับ")

finally:
    driver.quit()