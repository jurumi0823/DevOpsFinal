from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time

# 設置 Brave 瀏覽器
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.add_argument('--enable-automation')
options.add_argument('--disable-blink-features=AutomationControlled')

# 使用 ChromeDriver（適用於 Brave）
driver = webdriver.Chrome(options=options)

# 第一層 URL
base_url = "https://health.udn.com/health/disease_list"

# 初始化 CSV 文件
csv_file = "disease_data.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["疾病分類", "疾病名稱", "症狀", "併發症", "危險族群", "科別", "部位"])

def click_tab_and_extract_list_by_text(driver, tab_text):
    """
    通過導航欄中的文字點擊並提取對應的內容數據，處理元素遮擋問題。
    :param driver: Selenium WebDriver
    :param tab_text: 導航欄中的文字，例如 "症狀"、"併發症"
    :return: 提取到的數據列表，如果未找到對應的 Tab 返回 []
    """
    try:
        # 找到包含導航文字的所有選項
        tab_elements = driver.find_elements(By.CSS_SELECTOR, "div.splide__list a")
        tab_element = next((tab for tab in tab_elements if tab_text in tab.text), None)

        if not tab_element:
            print(f"Tab '{tab_text}' 不存在，跳過")
            return []  # 返回空列表
        
        # 滾動到可見範圍，處理可能的遮擋問題
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab_element)
        time.sleep(0.5)  # 給一點緩衝時間

        # 使用 JavaScript 點擊元素，避免遮擋問題
        driver.execute_script("arguments[0].click();", tab_element)
        time.sleep(1)  # 等待頁面更新

        # 找到對應的內容區域
        theme_id = tab_element.get_attribute("href").split("#")[-1]  # 提取 theme 的 ID，例如 "theme_1"
        content_elements = driver.find_elements(By.CSS_SELECTOR, f"article#{theme_id} ul li")

        return [item.text.strip() for item in content_elements if item.text.strip()]
    except Exception as e:
        print(f"通過文字 '{tab_text}' 抓取數據失敗: {e}")
        return []


# 定義目標導航文字列表
NAVIGATION_TABS = ["症狀", "併發症", "危險族群", "科別", "部位"]

# 提取數據的主程式邏輯
try:
    driver.get(base_url)
    print("打開第一層網頁...")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print("第一層頁面載入完成，開始抓取分類列表...")

    driver.execute_script("document.querySelectorAll('.sticky-ads, .ad-banner').forEach(el => el.style.display = 'none');")

    categories = driver.find_elements(By.CSS_SELECTOR, "nav.diseases-catalogue__group a")
    for cat_index in range(len(categories)):
        categories = driver.find_elements(By.CSS_SELECTOR, "nav.diseases-catalogue__group a")
        category = categories[cat_index]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", category)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(category))
        category_name = category.text
        print(f"進入分類 {cat_index + 1}/{len(categories)}: {category_name}")
        category.click()

        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "diseases-catalogue-list__group")))
        diseases = driver.find_elements(By.CSS_SELECTOR, "nav.diseases-catalogue-list__group a")

        for dis_index in range(len(diseases)):
            diseases = driver.find_elements(By.CSS_SELECTOR, "nav.diseases-catalogue-list__group a")
            disease = diseases[dis_index]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", disease)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(disease))
            disease_name = disease.get_attribute("title")  # 僅提取 title 的值
            print(f"  進入疾病 {dis_index + 1}/{len(diseases)}: {disease_name}")

            # 記錄返回第二層的 URL
            second_layer_url = driver.current_url

            disease.click()

            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "splide01")))
            
            # 動態提取每個導航 Tab 的數據
            data = {}
            for tab_text in NAVIGATION_TABS:
                data[tab_text] = click_tab_and_extract_list_by_text(driver, tab_text)

            # 將數據寫入 CSV
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    category_name, disease_name,
                    ",".join(data.get("症狀", [])) if data.get("症狀") else "null",
                    ",".join(data.get("併發症", [])) if data.get("併發症") else "null",
                    ",".join(data.get("危險族群", [])) if data.get("危險族群") else "null",
                    ",".join(data.get("科別", [])) if data.get("科別") else "null",
                    ",".join(data.get("部位", [])) if data.get("部位") else "null"
                ])
            print(f"  已保存疾病: {disease_name}")

            # 直接導航回第二層頁面
            driver.get(second_layer_url)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "diseases-catalogue-list__group")))

        # 返回第一層
        driver.get(base_url)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "nav.diseases-catalogue__group")))

finally:
    driver.quit()
    print("爬蟲完成，瀏覽器已關閉。")