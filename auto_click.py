from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# ========== 设置无头浏览器参数 ==========
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')

# ========== 创建 Chrome 驱动 ==========
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# ========== 日志配置 ==========
log_file = "click_log.txt"
log_retention_days = 2  # 日志保留天数

def clean_old_logs():
    if not os.path.exists(log_file):
        return
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        cleaned_lines = []
        cutoff = datetime.now() - timedelta(days=log_retention_days)
        for line in lines:
            if line.startswith("["):
                try:
                    ts = datetime.strptime(line.split("]")[0][1:], "%Y-%m-%d %H:%M:%S")
                    if ts >= cutoff:
                        cleaned_lines.append(line)
                except:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
    except Exception as e:
        print(f"日志清理失败：{e}")

# ========== 执行日志清理 ==========
clean_old_logs()

# ========== 主逻辑 ==========
try:
    driver.get("https://app-kfnreuvbhmi6ksaeksknf9.streamlit.app")
    print("✅ 页面已打开，等待加载 30 秒...")
    time.sleep(30)

    # ==== 进入 iframe（抱脸平台常用结构）====
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print(f"🌐 检测到 {len(iframes)} 个 iframe，进入第一个")
        driver.switch_to.frame(iframes[0])
        time.sleep(3)

    # ==== 查找包含 Yes 的按钮（更精准）====
    buttons = driver.find_elements(By.XPATH, "//button[contains(normalize-space(.), 'get this app back up')]")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if buttons:
        driver.execute_script("arguments[0].click();", buttons[0])
        print("✅ 检测到按钮，已点击，等待 45 秒恢复操作...")
        time.sleep(45)
        log_entry = f"[{timestamp}] ✅ 按钮已点击，已等待45秒完成\n"
    else:
        print("❌ 未检测到按钮，跳过点击")
        driver.save_screenshot("no_button_found.png")
        log_entry = f"[{timestamp}] ❌ 未发现按钮，未执行点击\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

except Exception as e:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{timestamp}] ❌ 脚本异常：{str(e)}\n"
    print(error_msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(error_msg)
    driver.save_screenshot("fatal_error.png")

finally:
    driver.quit()