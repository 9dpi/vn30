import json, requests, time
from datetime import datetime, timedelta, timezone

def fetch_yahoo(s):
    try:
        symbol = f"{s}.VN"
        end_ts = int(time.time())
        start_ts = int((datetime.now() - timedelta(days=30)).timestamp())
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if res.status_code == 200:
            data = res.json().get('chart', {}).get('result', [])[0]
            raw_close = data.get('indicators', {}).get('adjclose', [])[0].get('adjclose', [])
            close_p = [p for p in raw_close if p is not None]
            if len(close_p) >= 2:
                last_p, prev_p = close_p[-1], close_p[-2]
                change = round(((last_p - prev_p) / prev_p) * 100, 2)
                quote = data.get('indicators', {}).get('quote', [])[0]
                timestamps = data.get('timestamp', [])
                ohlc = []
                for i in range(len(timestamps)):
                    if quote['open'][i] is not None:
                        ohlc.append({
                            "x": datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                            "y": [quote['open'][i], quote['high'][i], quote['low'][i], close_p[i]]
                        })
                return {"p": round(last_p, 1), "c": change, "v": quote['volume'][-1], "chart": ohlc}
    except Exception as e:
        print(f"Bỏ qua {s}: {e}")
    return None

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    print("--- BẮT ĐẦU CẬP NHẬT VN30 ---")
    
    for s in tickers:
        data = fetch_yahoo(s)
        if data:
            results.append({
                "s": s, "p": data['p'], "c": data['c'], "v": data['v'],
                "f": "MUA" if data['c'] < -2.5 else ("BÁN" if data['c'] > 3 else "THEO DÕI"),
                "conf": 80 if abs(data['c']) > 2.5 else 65,
                "chart_data": data['chart']
            })
            print(f"[OK] {s}: {data['p']}")
        time.sleep(1)

    if results:
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        
        # FIX MÚI GIỜ VIỆT NAM (UTC+7)
        vn_tz = timezone(timedelta(hours=7))
        now_vn = datetime.now(vn_tz)
        
        # Nếu đã sau 15:00, dự báo dành cho ngày giao dịch tiếp theo
        f_date = now_vn + timedelta(days=1) if now_vn.hour >= 15 else now_vn
        while f_date.weekday() >= 5: f_date += timedelta(days=1)

        output = {
            "update_time": now_vn.strftime("%H:%M - %d/%m/%Y"),
            "forecast_for": f_date.strftime("%d/%m/%Y"),
            "stocks": results
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"--- BUILD THÀNH CÔNG: {output['forecast_for']} ---")

if __name__ == "__main__":
    get_market_data()
