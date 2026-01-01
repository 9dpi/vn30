import json
import requests
from datetime import datetime
import time

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    
    # Header đầy đủ để giả lập trình duyệt thật
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://vietstock.vn',
        'Referer': 'https://vietstock.vn/'
    }

    print("--- BẮT ĐẦU QUÉT DỮ LIỆU ---")
    
    for s in tickers:
        try:
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 30) 
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = requests.get(url, headers=headers, timeout=15)
            
            # Kiểm tra nếu phản hồi là JSON hợp lệ
            if res.status_code == 200:
                try:
                    data = res.json()
                except ValueError:
                    print(f"[LỖI ĐỊNH DẠNG] {s}: API không trả về JSON")
                    continue

                if isinstance(data, dict) and 'c' in data and len(data['c']) >= 2:
                    # Chuẩn bị dữ liệu nến
                    ohlc_data = []
                    for i in range(len(data['t'])):
                        ohlc_data.append({
                            "x": datetime.fromtimestamp(data['t'][i]).strftime('%Y-%m-%d'),
                            "y": [data['o'][i], data['h'][i], data['l'][i], data['c'][i]]
                        })
                    
                    last_p = data['c'][-1]
                    prev_p = data['c'][-2]
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    forecast = "THEO DÕI"
                    conf = 65
                    if change <= -2.5: forecast, conf = "MUA", 85
                    elif change >= 3.0: forecast, conf = "BÁN", 80

                    results.append({
                        "s": s, "p": last_p, "c": change, "v": data['v'][-1], 
                        "f": forecast, "conf": conf, "chart_data": ohlc_data 
                    })
                    print(f"[OK] {s}: {last_p}")
                else:
                    print(f"[THIẾU DỮ LIỆU] {s}: {data}")
            else:
                print(f"[LỖI HTTP] {s}: {res.status_code}")
                
            time.sleep(1) # Tăng thời gian nghỉ để tránh bị chặn IP
            
        except Exception as e:
            print(f"[LỖI HỆ THỐNG] {s}: {str(e)}")

    if results:
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        final_output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên tới",
            "stocks": results
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        print("--- THÀNH CÔNG ---")
    else:
        print("--- KHÔNG LẤY ĐƯỢC DỮ LIỆU ---")

if __name__ == "__main__":
    get_market_data()
