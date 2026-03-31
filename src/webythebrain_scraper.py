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
WE_CATALOG_URL = "https://store.webythebrain.com/course/"

# Helper Functions for Categorization
def categorize_subject(name):
    name = name.lower()
    if 'math' in name or 'คณิต' in name: return 'คณิตศาสตร์'
    if 'phy' in name or 'ฟิสิกส์' in name: return 'ฟิสิกส์'
    if 'bio' in name or 'ชีวะ' in name: return 'ชีววิทยา'
    if 'eng' in name or 'อังกฤษ' in name: return 'ภาษาอังกฤษ'
    if 'เคมี' in name: return 'เคมี'
    if 'tpat' in name or 'tgat' in name: return 'ความถนัด/TGAT/TPAT'
    if 'ไทย' in name: return 'ภาษาไทย'
    if 'สังคม' in name: return 'สังคมศึกษา'
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
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

all_course_links = set()

try:
    # --- STEP 1: Collect All Course Links from Catalog Pages ---
    print("--- Step 1: Collecting WE Course Links ---")
    driver.get(WE_CATALOG_URL)
    
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
            next_button.click()
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
            
            # Price
            try:
                # Find all prices, prefer discounted ones
                price_elements = driver.find_elements(By.CSS_SELECTOR, "span.woocommerce-Price-amount bdi, .course-price .current-price, .current-price")
                if price_elements:
                    price_text = price_elements[-1].text.strip()
                else:
                    price_text = "0"
            except:
                price_text = "0"
            
            price_val = float(re.sub(r'[^\d.]', '', price_text)) if re.sub(r'[^\d.]', '', price_text) else 0.0
            
            # Tutor
            tutor = "N/A"
            try:
                # In the provided HTML, tutors are in h5 tags inside wrap-auther-image-s
                # They might be hidden (display: none) so use get_attribute("textContent")
                tutor_elements = driver.find_elements(By.CSS_SELECTOR, ".wrap-auther-image-s h5, .wrap-auther-imagex h5, .wpt-instructor-s h5, .author-name-s h5")
                if tutor_elements:
                    tutor_names = []
                    for t in tutor_elements:
                        t_name = t.get_attribute("textContent").strip()
                        if t_name and t_name not in tutor_names:
                            tutor_names.append(t_name)
                    if tutor_names:
                        tutor = ", ".join(tutor_names)
                else:
                    # Fallback to we-tutor-card h4 if above fails
                    tutors = driver.find_elements(By.CSS_SELECTOR, "div.we-tutor-card h4")
                    if tutors:
                        tutor = ", ".join([t.get_attribute("textContent").strip() for t in tutors if t.get_attribute("textContent").strip()])
            except:
                pass
            
            # Total Hours
            total_hours = 0.0
            try:
                # Based on analysis, hours are often near "ชั่วโมงไฟล์การเรียน"
                hour_info_elements = driver.find_elements(By.CSS_SELECTOR, "div.summary-item")
                for item in hour_info_elements:
                    if "ชั่วโมงไฟล์การเรียน" in item.text:
                        hour_text = item.text
                        # Match formats like "40:00 ชม." or "40 ชม."
                        hour_match = re.search(r'([\d:]+)\s*ชม', hour_text)
                        if hour_match:
                            h_str = hour_match.group(1)
                            if ":" in h_str:
                                parts = h_str.split(":")
                                total_hours = float(parts[0]) + (float(parts[1])/60.0 if len(parts) > 1 else 0)
                            else:
                                total_hours = float(h_str)
                        break
            except:
                pass

            price_per_hour = price_val / total_hours if total_hours > 0 else 0.0

            row = {
                "institute_name": "WE By The Brain",
                "course_name": name,
                "tutor": tutor,
                "subject": categorize_subject(name),
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
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\nSaved {len(results)} courses to {output_file}")
    else:
        print("\nNo data collected.")

finally:
    driver.quit()
