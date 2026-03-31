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

# --- Input: WE Course Catalog URL ---
WE_CATALOG_URL = "https://store.webythebrain.com/course/?utm_source=google&utm_medium=cpc&utm_campaign=ads_courses&utm_content=20250111_individualcourses&gad_source=1&gad_campaignid=22112613317&gbraid=0AAAAAprrK5nvznhKnrpaLtAETiL30mGVe&gclid=CjwKCAjwvqjOBhAGEiwAngeQna-QgtYereNoKxejeHddZNiJXOvcg1Mp3IAY7Xul7nPsjQx1GP74hhoCwPQQAvD_BwE"

# Helper Functions for Categorization
def categorize_subject(name, breadcrumb=""):
    combined_text = (name + " " + breadcrumb).lower()
    if 'math' in combined_text or 'คณิต' in combined_text: return 'คณิตศาสตร์'
    if 'phy' in combined_text or 'ฟิสิกส์' in combined_text: return 'ฟิสิกส์'
    if 'bio' in combined_text or 'ชีวะ' in combined_text or 'ชีววิทยา' in combined_text: return 'ชีววิทยา'
    if 'eng' in combined_text or 'อังกฤษ' in combined_text: return 'ภาษาอังกฤษ'
    if 'เคมี' in combined_text: return 'เคมี'
    if 'tpat' in combined_text or 'tgat' in combined_text: return 'ความถนัด/TGAT/TPAT'
    if 'ไทย' in combined_text: return 'ภาษาไทย'
    if 'สังคม' in combined_text: return 'สังคมศึกษา'
    return 'อื่นๆ'

def categorize_type(name):
    name = name.lower()
    if 'alevel' in name or 'ติวสอบ' in name or 'tcas' in name or 'check up' in name: return 'ติวสอบ A-Level/TCAS'
    if 'pack' in name or 'แพ็ก' in name: return 'คอร์สแพ็กเกจ'
    if 'ปูพื้นฐาน' in name or 'basic' in name: return 'ปูพื้นฐาน'
    if 'เข้า ม.4' in name or 'mwit' in name or 'kvis' in name: return 'สอบเข้า ม.4'
    if 'เข้า ม.1' in name: return 'สอบเข้า ม.1'
    return 'ติวเนื้อหา/เสริมเกรด'

# Setup Selenium
chrome_options = Options()
# chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

all_course_links = set()

try:
    # --- STEP 1: Collect All Course Links from Catalog Pages ---
    print("--- Step 1: Collecting WE Course Links ---")
    driver.get(WE_CATALOG_URL)
    
    # --- [เพิ่มใหม่] กด Filter ระดับชั้น ---
    print("กำลังตั้งค่า Filter ระดับชั้น...")
    time.sleep(3) # รอให้หน้าเว็บโหลดโครงสร้างเสร็จ
    
    # รายชื่อ value ของ checkbox ที่เราต้องการติ๊ก (ม.ปลาย และ สอบเข้ามหาลัย)
    target_filters = ["university-admission", "senior-high-school"]
    
    for val in target_filters:
        try:
            # หา input ที่มีค่า value ตรงกับที่เราต้องการ
            checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"input[type='checkbox'][value='{val}']")))
            
            # ใช้ JavaScript คลิกลดปัญหา Element โดนบัง
            driver.execute_script("arguments[0].click();", checkbox)
            print(f"  [+] ติ๊ก Filter: {val} เรียบร้อยแล้ว")
            time.sleep(2) # รอให้เว็บหมุนโหลดข้อมูลคอร์สชุดใหม่
        except Exception as e:
            print(f"  [-] ไม่สามารถติ๊ก Filter {val} ได้: {e}")

    print("เริ่มกวาดลิงก์คอร์สเรียน...")
    # ------------------------------------

    page_num = 1
    while True:
        print(f"Scraping links from page {page_num}...")
        time.sleep(3) # Wait for AJAX content
        
        # Extract course links
        course_elements = driver.find_elements(By.CSS_SELECTOR, "h3.course-title a")
        links_added = 0
        for elem in course_elements:
            link = elem.get_attribute("href")
            if link and link not in all_course_links:
                all_course_links.add(link)
                links_added += 1
        
        print(f"Found {links_added} new links (Total: {len(all_course_links)})")
        
        # Try to click "Next" button
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "button.we-page-next")
            if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                print("Reach last page.")
                break
            
            # Scroll to button and click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)
            # ใช้ JS click กับปุ่ม Next ด้วยเลยเพื่อความชัวร์
            driver.execute_script("arguments[0].click();", next_button)
            page_num += 1
        except Exception as e:
            print("No 'Next' button found or error clicking it. Finishing link collection.")
            break

    course_list = list(all_course_links)
    print(f"Total unique courses found: {len(course_list)}")

    # --- STEP 2: Scrape Details for Each Course ---
    print("\n--- Step 2: Scraping Details ---")
    results = []

    for index, course_url in enumerate(course_list, 1):
        # Limit for initial testing
        # if index > 10: break
        
        print(f"({index}/{len(course_list)}) Scraping: {course_url}")
        try:
            driver.get(course_url)
            time.sleep(2)
            
            # Course Name
            try:
                # Primary choice: h1 inside course-title-wrap or h1 with course-title/product_title class
                name_elem = driver.find_element(By.CSS_SELECTOR, ".course-title-wrap h1, h1.course-title, h1.product_title")
                name = name_elem.get_attribute("textContent").strip()
            except:
                try:
                    name = driver.find_element(By.CSS_SELECTOR, "h1").get_attribute("textContent").strip()
                except:
                    name = "N/A"
            
            # --- Price Extraction ---
            price_val = 0.0
            try:
                # Try common UI elements first
                price_elem = None
                selectors = [
                    ".woocommerce-Price-amount bdi", 
                    ".current-price", 
                    ".course-price .current-price",
                    "ins .woocommerce-Price-amount bdi"
                ]
                for sel in selectors:
                    try:
                        price_elem = driver.find_element(By.CSS_SELECTOR, sel)
                        if price_elem: break
                    except: continue
                
                if price_elem:
                    price_text = price_elem.get_attribute("textContent").strip()
                else:
                    # Try meta tag
                    try:
                        price_elem = driver.find_element(By.CSS_SELECTOR, "meta[property='product:price:amount']")
                        price_text = price_elem.get_attribute("content")
                    except:
                        price_text = "0"
                
                price_val = float(re.sub(r'[^\d.]', '', price_text)) if re.sub(r'[^\d.]', '', price_text) else 0.0
            except:
                price_val = 0.0
            
            # --- Tutor Extraction ---
            tutor = "N/A"
            try:
                tutor_elements = driver.find_elements(By.CSS_SELECTOR, ".wrap-auther-image-s h5, .wrap-auther-imagex h5, .wpt-instructor-s h5, .author-name-s h5")
                if tutor_elements:
                    tutor_names = []
                    for t in tutor_elements:
                        t_name = t.get_attribute("textContent").strip()
                        if t_name and t_name not in tutor_names:
                            tutor_names.append(t_name)
                    if tutor_names:
                        tutor = ", ".join(tutor_names)
            except:
                pass
            
            # --- Total Hours Extraction ---
            total_hours = 0.0
            try:
                # Use a broad search on page source text for better reliability
                page_text = driver.execute_script("return document.body.textContent;")
                
                # Search for "ชั่วโมงไฟล์การเรียน"
                hour_match = re.search(r'ชั่วโมงไฟล์การเรียน\s*([\d:]+)\s*ชม', page_text)
                if hour_match:
                    h_str = hour_match.group(1)
                    if ":" in h_str:
                        parts = h_str.split(":")
                        total_hours = float(parts[0]) + (float(parts[1])/60.0 if len(parts) > 1 else 0)
                    else:
                        total_hours = float(h_str)
                
                # Fallback if still 0
                if total_hours == 0:
                    fallback_match = re.search(r'(\d+)\s*ชั่วโมง', page_text)
                    if fallback_match:
                        total_hours = float(fallback_match.group(1))
            except:
                pass

            # [เพิ่มใหม่] ดึงข้อมูล Breadcrumb เพื่อช่วยจัดหมวดหมู่วิชา
            breadcrumb_text = ""
            try:
                breadcrumb_elem = driver.find_element(By.CSS_SELECTOR, "nav.woocommerce-breadcrumb, .sl-breadcrumb-mb nav")
                breadcrumb_text = breadcrumb_elem.get_attribute("textContent").strip()
            except:
                pass

            price_per_hour = price_val / total_hours if total_hours > 0 else 0.0

            row = {
                "institute_name": "WE By The Brain",
                "course_name": name,
                "tutor": tutor,
                "subject": categorize_subject(name, breadcrumb_text),
                "course_type": categorize_type(name),
                "learning_format": "วิดีโอ (ออนไลน์/สาขา)",
                "total_hours": round(total_hours, 2),
                "price": price_val,
                "price_per_hour": round(price_per_hour, 2),
                "url": course_url
            }
            results.append(row)
            
        except Exception as e:
            print(f"Error scraping {course_url}: {e}")

    # --- STEP 3: Save to CSV ---
    if results:
        df = pd.DataFrame(results)
        output_file = "../data/we_courses.csv"
        
        # Ensure directory exists
        dir_name = os.path.dirname(output_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\nSaved {len(results)} courses to {output_file}")
    else:
        print("\nNo data collected.")

finally:
    driver.quit()
