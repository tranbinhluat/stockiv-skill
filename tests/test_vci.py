import datetime
from vnstock import Quote, Company

def test_vci():
    print("Testing Quote history for VNINDEX with VCI...")
    try:
        quote = Quote(symbol="VNINDEX", source="VCI")
        df = quote.history(start="2026-03-01", end="2026-03-07", interval="1D")
        print(df)
    except Exception as e:
        print(f"Error Quote VNINDEX: {e}")

    print("\nTesting Company ratio_summary for VNINDEX with VCI...")
    try:
        company = Company(symbol="VNINDEX", source="VCI")
        df = company.ratio_summary()
        print(df)
    except Exception as e:
        print(f"Error ratio_summary VNINDEX: {e}")

    print("\nTesting Company events for VNINDEX with VCI...")
    try:
        company = Company(symbol="VNINDEX", source="VCI")
        df = company.events()
        print(df)
    except Exception as e:
        print(f"Error events VNINDEX: {e}")

if __name__ == "__main__":
    test_vci()
