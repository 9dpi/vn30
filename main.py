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
            json_data = res.json()
            result = json_data.get('chart', {}).get('result')
            
            # KIỂM TRA DỮ LIỆU CÓ TỒN TẠI KHÔNG
            if not result or len(result) == 0:
                return None
                
            data = result[0]
            indicators = data.get('indicators', {}).get('adjclose', [{}])[0]
            raw_close = indicators.get('adjclose', [])
            
            # Loại bỏ các giá trị None
            close_p = [p for p in raw_close if p is not None]
            
            if len(close_p) >= 2:
                last_p, prev_p = close_p[-1], close_p[-2]
                change = round(((last_p - prev_p) / prev_p) * 100, 2)
                
                quote = data.get('indicators', {}).get('quote', [{}])[0]
                timestamps = data.get('timestamp', [])
                
                ohlc = []
                # Đảm bảo các danh sách dữ liệu có cùng độ dài
                for i in range(min(len(timestamps), len(quote.get('open', [])))):
                    if quote['open'][i] is not None and i < len(close_p):
                        ohlc.append({
                            "x": datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d'),
                            "y": [quote['open'][i], quote['high'][i], quote['low'][i], close_p[i]]
                        })
                
                return {
                    "p": round(last_p, 1), 
                    "c": change, 
                    "v": quote.get('volume', [0])[-1] if quote.get('volume') else 0, 
                    "chart": ohlc
                }
    except Exception as e:
        print(f"Lỗi tại {s}: {e}")
    return None

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    print("--- BẮT ĐẦU CẬP NHẬT VN30 ---")
    
    for s in tickers:
        data = fetch_yahoo(s)
        if data:
            # Logic phân loại AI Signal
            signal = "THEO DÕI"
            if data['c'] < -2.0: signal = "MUA"
            elif data['c'] > 2.5: signal = "BÁN"
            
            results.append({
                "s": s, "p": data['p'], "c": data['c'], "v": data['v'],
                "f": signal,
                "conf": 80 if abs(data['c']) > 2.0 else 65,
                "chart_data": data['chart']
            })
            print(f"[OK] {s}: {data['p']}")
        time.sleep(0.5) # Giảm thời gian chờ để tránh timeout

    if results:
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        vn_tz = timezone(timedelta(hours=7))
        now_vn = datetime.now(vn_tz)
        
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
