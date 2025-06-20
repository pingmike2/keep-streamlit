from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# 设置无头浏览器参数
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

# 创建 Chrome 驱动
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 日志配置
log_file = "click_log.txt"
log_retention_days = 2  # 日志保留天数

# 清理旧日志
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
                    timestamp_str = line.split("]")[0][1:]
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    if timestamp >= cutoff:
                        cleaned_lines.append(line)
                except:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)

        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)

    except Exception as e:
        print(f"日志清理失败：{e}")

# 执行清理
clean_old_logs()

# 开始主逻辑
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_entry = f"[{timestamp}] 开始访问页面\n"

try:
    url = "https://app-kfnreuvbhmi6ksaeksknf9.streamlit.app"
    driver.get(url)
    print("✅ 页面已打开，等待加载 30 秒...")
    time.sleep(30)

    # 检测 iframe 并切入
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print(f"🌐 检测到 {len(iframes)} 个 iframe，切入第一个")
        driver.switch_to.frame(iframes[0])

    # Step 1: 尝试点击 “get this app back up”
    try:
        back_up_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'get this app back up')]"))
        )
        back_up_btn.click()
        print("🟢 已点击 'get this app back up' 按钮，等待唤醒...")
        log_entry += f"[{timestamp}] 点击了 'get this app back up'\n"
        time.sleep(45)

        # Step 2: 再尝试点击 “启动部署”
        try:
            deploy_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., '启动部署')]"))
            )
            deploy_btn.click()
            print("✅ 已点击 '启动部署' 按钮。")
            log_entry += f"[{timestamp}] 成功点击 '启动部署'\n"
        except Exception as e:
            print("⚠️ 未检测到 '启动部署' 按钮。")
            log_entry += f"[{timestamp}] 未检测到 '启动部署'：{str(e)}\n"

    except Exception:
        print("❌ 未检测到 'get this app back up'，不执行启动部署")
        log_entry += f"[{timestamp}] 页面正常，无需唤醒\n"

    # 写入日志
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

except Exception as e:
    print(f"发生错误：{e}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 脚本异常：{str(e)}\n")
    driver.save_screenshot("debug.png")

finally:
    driver.quit()