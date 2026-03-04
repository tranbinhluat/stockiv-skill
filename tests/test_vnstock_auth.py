import os
from vnstock import Finance

print("API Key Present:", "Yes" if os.environ.get("VNSTOCK_API_KEY") else "No")

print("\nTesting Finance with KBS source...")
try:
    finance = Finance(symbol="VCI", source="KBS")
    df = finance.balance_sheet(period="quarter")
    print("Success! Shape:", df.shape)
    print(df.head(2))
except Exception as e:
    print("Error with KBS:", e)

print("\nTesting Finance with VCI source...")
try:
    finance_vci = Finance(symbol="VCI", source="VCI")
    df_vci = finance_vci.balance_sheet(period="quarter")
    print("Success! Shape:", df_vci.shape)
    print(df_vci.head(2))
except Exception as e:
    print("Error with VCI:", e)
