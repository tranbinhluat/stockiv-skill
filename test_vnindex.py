from vnstock import Quote
try:
    for src in ["TCBS", "VND", "VCI"]:
        try:
            q = Quote(symbol="VNINDEX", source=src)
            df = q.history(interval="1D")
            if df is not None and not df.empty:
                print(f"Success with {src}")
                print(df.tail())
                break
        except Exception as e:
            continue
except Exception as e:
    print(e)
