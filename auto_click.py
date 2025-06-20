from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import os

# 设置无头浏览器参数
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 创建 Chrome 驱动
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# 日志配置
log_file = "click_log.txt"
log_retention_days = 2  # 日志保留天数

# 清理旧日志函数
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
                    cleaned_lines.append(line)  # 非时间行保留
            else:
                cleaned_lines.append(line)

        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)

    except Exception as e:
        print(f"日志清理失败：{e}")

# 执行清理
clean_old_logs()

# 主逻辑开始
try:
    driver.get("https://app-kfnreuvbhmi6ksaeksknf9.streamlit.app")
    print("✅ 页面已打开，等待加载 30 秒...")
    time.sleep(30)

    # 检查 iframe 并切入
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        print(f"🌐 检测到 {len(iframes)} 个 iframe，切入第一个")
        driver.switch_to.frame(iframes[0])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Step 1: 检测并点击 “Yes, get this app back up!”
    back_btns = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'get this app back up')]")
    if back_btns:
        print("✅ 检测到 'get this app back up'，开始点击...")
        back_btns[0].click()
        time.sleep(45)
        log_entry = f"[{timestamp}] 已点击 'get this app back up' 并等待 45 秒\n"

        # Step 2: 检查并点击“启动部署”
        deploy_btns = driver.find_elements(By.XPATH, "//button[contains(text(), '启动部署')]")
        if deploy_btns:
            deploy_btns[0].click()
            print("🚀 已点击 '启动部署' 按钮。")
            log_entry += f"[{timestamp}] 已点击 '启动部署' 按钮\n"
        else:
            print("⚠️ 未找到 '启动部署' 按钮")
            log_entry += f"[{timestamp}] 未找到 '启动部署' 按钮\n"
    else:
        print("❌ 未检测到 'get this app back up'，不执行启动部署")
        log_entry = f"[{timestamp}] 未检测到唤醒按钮，未执行部署操作\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

except Exception as e:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{timestamp}] 错误：{str(e)}\n"
    print(f"发生错误：{e}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(error_msg)
    driver.save_screenshot("debug.png")

finally:
    driver.quit()