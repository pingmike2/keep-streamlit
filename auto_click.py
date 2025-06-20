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

# 主逻辑部分

try:
    driver.get("https://app-kfnreuvbhmi6ksaeksknf9.streamlit.app/")
    print("已打开网页，等待页面加载 30 秒...")
    time.sleep(30)  # 初次加载等待

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 先找“get this app back up”按钮
    back_up_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'get this app back up')]")
    if back_up_buttons:
        back_up_buttons[0].click()
        print("检测到 'get this app back up' 按钮，已点击。等待 30 秒...")
        time.sleep(30)

        # 点完“get this app back up”后再找“启动部署”按钮
        deploy_buttons = driver.find_elements(By.XPATH, "//button[contains(., '启动部署')]")
        if deploy_buttons:
            deploy_buttons[0].click()
            print("检测到 '启动部署' 按钮，已点击。")
            log_entry = f"[{timestamp}] 先点击了 'get this app back up'，等待30秒后点击了 '启动部署'\n"
        else:
            print("未检测到 '启动部署' 按钮。")
            log_entry = f"[{timestamp}] 点击了 'get this app back up'，但未发现 '启动部署' 按钮\n"
    else:
        # 如果没找到“get this app back up”，直接点“启动部署”
        deploy_buttons = driver.find_elements(By.XPATH, "//button[contains(., '启动部署')]")
        if deploy_buttons:
            deploy_buttons[0].click()
            print("未发现 'get this app back up' 按钮，检测到 '启动部署' 按钮，已点击。")
            log_entry = f"[{timestamp}] 未发现 'get this app back up'，直接点击了 '启动部署'\n"
        else:
            print("未检测到任何目标按钮，跳过点击。")
            log_entry = f"[{timestamp}] 未发现任何目标按钮，未执行点击\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)

except Exception as e:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{timestamp}] 错误：{str(e)}\n"
    print(f"发生错误：{e}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(error_msg)

finally:
    driver.quit()