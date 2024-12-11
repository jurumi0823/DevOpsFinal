import requests
import random
import time
from threading import Thread

# 要測試的目標 URL
base_url = "http://127.0.0.1:5001"

# 模擬的錯誤請求
def simulate_error_request():
    endpoint = "/nonexistent" # 隨機選擇一個錯誤路徑
    try:
        response = requests.get(base_url + endpoint)
        print(f"Request to {endpoint} returned status: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error occurred: {e}")

# 每秒模擬 1~10 個錯誤請求
def run_requests_per_second():
    while True:
        num_requests = random.randint(1, 10)  # 每秒隨機發送 1~10 個請求
        threads = []

        # 創建多個線程以同時發送請求
        for _ in range(num_requests):
            thread = Thread(target=simulate_error_request)
            threads.append(thread)
            thread.start()

        # 等待所有線程完成
        for thread in threads:
            thread.join()

        print(f"Sent {num_requests} requests this second")
        time.sleep(1)  # 每秒執行一次

# 主程式
if __name__ == "__main__":
    run_requests_per_second()
