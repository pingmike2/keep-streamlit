from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import os
import time

# 设置日志文件
log_file = "click_log.txt"
log_retention_days = 2

# 清理旧日志
def clean_old_logs():
    if not os.path.exists(log_file):
        return
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        cutoff = datetime.now() - timedelta(days=log_retention_days)
        cleaned = []
        for line in lines:
            if line.startswith("["):
                try:
                    t = line.split("]")[0][1:]
                    if datetime.strptime(t, "%Y-%m-%d %H:%M:%S") >= cutoff:
                        cleaned.append(line)
                except:
                    cleaned.append(line)
            else:
                cleaned.append(line)
        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(cleaned)
    except Exception as e:
        print(f"日志清理失败: {e}")

# 初始化浏览器
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
options.add_argument('--headless')  # GitHub Actions 必须无头

driver = None
clean_old_logs()

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    url = "https://app-kfnreuvbhmi6ksaeksknf9.streamlit.app/"
    driver.get(url)

    print("已打开网页，等待页面加载 30 秒...")
    time.sleep(30)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 检测 iframe（如果存在，切进去）
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if len(iframes) > 0:
        print(f"检测到 {len(iframes)} 个 iframe，尝试切入第一个。")
        driver.switch_to.frame(iframes[0])

    log_entry = ""

    # Step 1: 尝试点击 “get this app back up”
    found_get_back = False
    try:
        back_up_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'get this app back up')]"))
        )
        driver.execute_script("arguments[0].click();", back_up_btn)
        print("已点击 'get this app back up'，等待 30 秒...")
        time.sleep(30)
        found_get_back = True
        log_entry += f"[{timestamp}] 点击了 'get this app back up' 按钮\n"
    except:
        print("未检测到 'get this app back up' 按钮，跳过 '启动部署'。")
        log_entry += f"[{timestamp}] 未检测到 'get this app back up'，不尝试启动部署\n"

    # Step 2: 如果成功点击了 get this app back up，再尝试点击 “启动部署”
    if found_get_back:
        try:
            deploy_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., '启动部署')]"))
            )
            driver.execute_script("arguments[0].click();", deploy_btn)
            print("已点击 '启动部署' 按钮。")
            log_entry += f"[{timestamp}] 成功点击 '启动部署'\n"
        except Exception as e:
            print("未检测到 '启动部署' 按钮或点击失败。")
            log_entry += f"[{timestamp}] 未检测到 '启动部署' 或点击失败：{str(e)}\n"
            driver.save_screenshot("debug.png")

    # 写入日志
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

except Exception as e:
    print(f"发生错误：{e}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 脚本异常：{str(e)}\n")
    if driver:
        driver.save_screenshot("debug.png")

finally:
    if driver:
        driver.quit()