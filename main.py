import json
import requests
from datetime import datetime, timedelta
import time

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    print("--- QUÉT DỮ LIỆU LỊCH SỬ ĐỂ ĐẢM BẢO LUÔN CÓ DATA ---")
    
    for s in tickers:
        try:
            # Lấy 15 ngày để bao phủ các ngày nghỉ
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 15) 
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if data and 'c' in data and len(data['c']) >= 2:
                    last_p = data['c'][-1]
                    prev_p = data['c'][-2]
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    forecast = "THEO DÕI"
                    conf = 65
                    if change <= -2.5: forecast, conf = "MUA", 85
                    elif change >= 3.0: forecast, conf = "BÁN", 80

                    results.append({"s": s, "p": last_p, "c": change, "v": data['v'][-1], "f": forecast, "conf": conf})
            time.sleep(0.2)
        except: continue

    if results:
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({"update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"), "forecast_for": "Phiên tới", "stocks": results}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_market_data()
