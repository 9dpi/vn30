import json
import requests
from datetime import datetime
import time

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    
    # Header cực kỳ chi tiết để vượt lỗi 403
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        'Origin': 'https://vietstock.vn',
        'Referer': 'https://vietstock.vn/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
    }

    print("--- ĐANG THỬ NGHIỆM PHƯƠNG THỨC TRUY CẬP MỚI ---")
    
    # Sử dụng Session để giữ Cookie, tăng độ tin cậy với Server
    session = requests.Session()
    session.headers.update(headers)

    for s in tickers:
        try:
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 30)
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = session.get(url, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                if data and 'c' in data and len(data['c']) >= 2:
                    ohlc = [{"x": datetime.fromtimestamp(data['t'][i]).strftime('%Y-%m-%d'), 
                             "y": [data['o'][i], data['h'][i], data['l'][i], data['c'][i]]} for i in range(len(data['t']))]
                    
                    last_p, prev_p = data['c'][-1], data['c'][-2]
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    results.append({
                        "s": s, "p": last_p, "c": change, "v": data['v'][-1],
                        "f": "MUA" if change < -2.5 else ("BÁN" if change > 3 else "THEO DÕI"),
                        "conf": 80 if abs(change) > 2.5 else 65,
                        "chart_data": ohlc
                    })
                    print(f"[THÀNH CÔNG] {s}: {last_p}")
            else:
                print(f"[BỊ CHẶN {res.status_code}] {s}")
            
            # Nghỉ lâu hơn một chút để server không nghi ngờ
            time.sleep(1.2)
            
        except Exception as e:
            print(f"[LỖI] {s}: {str(e)}")

    if results:
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({"update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"), 
                       "forecast_for": "Phiên tới", "stocks": results}, f, ensure_ascii=False, indent=2)
        print("--- ĐÃ CẬP NHẬT DỮ LIỆU ---")

if __name__ == "__main__":
    get_market_data()
