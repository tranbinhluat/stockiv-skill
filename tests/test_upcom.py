import requests

url = (
    "https://static2.vietstock.vn/data/UPCOM/2023/BCTN/VN/MCH_Baocaothuongnien_2023.pdf"
)
print(f"UPCOM MCH 2023: {requests.head(url).status_code}")

url2 = "https://static2.vietstock.vn/data/UPCOME/2023/BCTN/VN/MCH_Baocaothuongnien_2023.pdf"
print(f"UPCOME MCH 2023: {requests.head(url2).status_code}")
