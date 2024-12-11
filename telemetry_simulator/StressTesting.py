import requests
from concurrent.futures import ThreadPoolExecutor

# 要測試的伺服器地址
url = "http://127.0.0.1:5001/"

# 發送請求的函數
def send_request():
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error: {e}")

# 高併發測試
if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=100) as executor:  # 100 個線程模擬併發
        for _ in range(5000):  # 發送 1000 次請求
            executor.submit(send_request)
