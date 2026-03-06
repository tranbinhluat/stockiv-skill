import requests

url = "https://static2.vietstock.vn/data/HNX/2025/BCTN/VN/PMT_Baocaothuongnien_2025.pdf"
response = requests.head(url)
print(f"Status for PMT: {response.status_code}")

url2 = (
    "https://static2.vietstock.vn/data/HOSE/2024/BCTN/VN/FPT_Baocaothuongnien_2024.pdf"
)
response2 = requests.head(url2)
print(f"Status for FPT HOSE: {response2.status_code}")

url3 = (
    "https://static2.vietstock.vn/data/HOSE/2023/BCTN/VN/FPT_Baocaothuongnien_2023.pdf"
)
response3 = requests.head(url3)
print(f"Status for FPT 2023 HOSE: {response3.status_code}")
