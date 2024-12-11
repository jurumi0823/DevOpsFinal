import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor

# 要發送請求的目標 URL
url = "http://127.0.0.1:5001/"  # 替換成你的網頁地址

# 發送請求的函數
def send_request():
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error: {e}")

# 主程序
if __name__ == "__main__":
    while True:
        # 隨機生成 1 到 10 次請求的數量
        num_requests = random.randint(1, 10)
        print(f"Sending {num_requests} requests in this second...")

        # 使用多線程來並行發送請求
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            for _ in range(num_requests):
                executor.submit(send_request)

        time.sleep(1)  # 每隔 1 秒執行一次
