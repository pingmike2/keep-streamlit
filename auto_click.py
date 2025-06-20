from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# ✅ 设置无头浏览器参数
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

log_file = "click_log.txt"
log_retention_days = 2

# ✅ 清理旧日志
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

clean_old_logs()

# ✅ 主逻辑
try:
    url = "https://app-kfnreuvbhmi6ksaeksknf9.streamlit.app"
    driver.get(url)
    print("✅ 页面已打开，等待加载 30 秒...")
    time.sleep(30)

    # 🔍 检查 iframe
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print("🌐 检测到 iframe，切入第一个")
        driver.switch_to.frame(iframes[0])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] 打开页面 {url}\n"

    # ✅ 检测按钮（兼容大小写、空格）
    buttons = driver.find_elements(By.XPATH,
        "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'get this app back up')]")

    if buttons:
        print("🟢 检测到按钮，点击中...")
        buttons[0].click()
        time.sleep(45)
        log_entry += f"[{timestamp}] 成功点击 get this app back up 并等待 45 秒\n"
    else:
        print("❌ 未检测到按钮，跳过点击")
        log_entry += f"[{timestamp}] 未检测到按钮，未执行点击\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

except Exception as e:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"❗️发生错误：{e}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 脚本异常：{str(e)}\n")
    driver.save_screenshot("debug.png")

finally:
    driver.quit()