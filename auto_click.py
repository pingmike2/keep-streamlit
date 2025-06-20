from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# ========== 配置无头浏览器 ==========
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# ========== 创建 Chrome 实例 ==========
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# ========== 日志配置 ==========
log_file = "click_log.txt"
log_retention_days = 2

def clean_old_logs():
    if not os.path.exists(log_file):
        return
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        cleaned = []
        cutoff = datetime.now() - timedelta(days=log_retention_days)
        for line in lines:
            if line.startswith("["):
                try:
                    ts = datetime.strptime(line.split("]")[0][1:], "%Y-%m-%d %H:%M:%S")
                    if ts >= cutoff:
                        cleaned.append(line)
                except:
                    cleaned.append(line)
            else:
                cleaned.append(line)
        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(cleaned)
    except Exception as e:
        print(f"日志清理失败：{e}")

# ========== 执行清理 ==========
clean_old_logs()

try:
    url = "https://app-kfnreuvbhmi6ksaeksknf9.streamlit.app"
    driver.get(url)
    print("✅ 页面已打开，等待加载 30 秒...")
    time.sleep(30)

    # ==== 进入 iframe（如果有）====
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print(f"🌐 检测到 {len(iframes)} 个 iframe，切入第一个")
        driver.switch_to.frame(iframes[0])
        time.sleep(2)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = ""

    # ==== Step 1: 检查并点击 "get this app back up" ====
    found_back_up = False
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        if "get this app back up" in btn.text.lower():
            btn.click()
            found_back_up = True
            print("✅ 点击了 'get this app back up' 按钮，等待 45 秒...")
            log_entry += f"[{timestamp}] 点击 'get this app back up' 按钮\n"
            time.sleep(45)
            break

    # ==== Step 2: 只有点击了 back up 按钮才去点 “启动部署” ====
    if found_back_up:
        deploy_buttons = driver.find_elements(By.TAG_NAME, "button")
        deploy_clicked = False
        for btn in deploy_buttons:
            if "启动部署" in btn.text:
                btn.click()
                print("✅ 点击了 '启动部署'")
                log_entry += f"[{timestamp}] 点击 '启动部署' 按钮\n"
                deploy_clicked = True
                break
        if not deploy_clicked:
            print("⚠️ 未找到 '启动部署' 按钮")
            log_entry += f"[{timestamp}] 未找到 '启动部署' 按钮\n"
    else:
        print("❌ 未检测到 'get this app back up'，不执行启动部署")
        log_entry += f"[{timestamp}] 未检测到 'get this app back up'，未执行任何操作\n"

    # 写入日志
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

except Exception as e:
    print(f"💥 发生错误：{e}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 脚本异常：{str(e)}\n")
    driver.save_screenshot("error.png")

finally:
    driver.quit()