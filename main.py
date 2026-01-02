import json, requests, time
from datetime import datetime, timedelta

def fetch_from_yahoo(s):
    # Chuyển đổi mã sang định dạng Yahoo (ví dụ: FPT -> FPT.VN)
    symbol = f"{s}.VN"
    end_ts = int(time.time())
    start_ts = int((datetime.now() - timedelta(days=30)).timestamp())
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            result = data.get('chart', {}).get('result', [])[0]
            timestamps = result.get('timestamp', [])
            quote = result.get('indicators', {}).get('quote', [])[0]
            adj_close = result.get('indicators', {}).get('adjclose', [])[0].get('adjclose', [])

            if len(adj_close) >= 2:
                # Chuẩn bị dữ liệu OHLC
                ohlc = []
                for i in range(len(timestamps)):
                    if quote['open'][i] is not None:
                        ohlc.append({
                            "x": datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                            "y": [round(quote['open'][i], 1), round(quote['high'][i], 1), 
                                  round(quote['low'][i], 1), round(adj_close[i], 1)]
                        })
                
                last_p = round(adj_close[-1], 1)
                prev_p = round(adj_close[-2], 1)
                change = round(((last_p - prev_p) / prev_p) * 100, 2)
                
                return {"p": last_p, "c": change, "v": quote['volume'][-1], "chart": ohlc}
    except Exception:
        pass
    return None

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    
    print("--- TRUY XUẤT DỮ LIỆU TỪ YAHOO FINANCE ---")

    for s in tickers:
        data = fetch_from_yahoo(s)
        if data:
            results.append({
                "s": s, "p": data['p'], "c": data['c'], "v": data['v'],
                "f": "MUA" if data['c'] < -2.0 else ("BÁN" if data['c'] > 2.0 else "THEO DÕI"),
                "conf": 80 if abs(data['c']) > 2.0 else 65,
                "chart_data": data['chart']
            })
            print(f"[OK] {s}: {data['p']} ({data['c']}%)")
        else:
            print(f"[FAIL] {s}: Không thể lấy dữ liệu từ Yahoo.")
        time.sleep(0.5)

    if results:
        # Sắp xếp theo biến động mạnh nhất lên đầu
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "stocks": results
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"--- THÀNH CÔNG: ĐÃ CẬP NHẬT {len(results)} MÃ ---")

if __name__ == "__main__":
    get_market_data()
