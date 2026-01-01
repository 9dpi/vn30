import json
import requests
from datetime import datetime, timedelta
import time

def get_market_data():
    # 30 mã VN30 hot nhất
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    print(f"--- ĐANG QUÉT DỮ LIỆU LỊCH SỬ ---")
    
    for s in tickers:
        try:
            # Lấy dữ liệu 10 ngày gần nhất để đảm bảo có data kể cả ngày lễ
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 15) 
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if data and 'c' in data and len(data['c']) >= 2:
                    prices = data['c']
                    volumes = data['v']
                    
                    last_p = prices[-1] # Giá đóng cửa phiên gần nhất
                    prev_p = prices[-2] # Giá đóng cửa phiên trước đó
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    # Thuật toán dự báo dựa trên biến động 3 phiên gần nhất
                    avg_3 = sum(prices[-3:]) / 3
                    forecast = "THEO DÕI"
                    conf = 65
                    
                    if last_p < avg_3 and change < -1:
                        forecast = "MUA"
                        conf = 85
                    elif last_p > avg_3 and change > 1.5:
                        forecast = "BÁN"
                        conf = 80
                    elif abs(change) < 0.5:
                        forecast = "GIỮ"
                        conf = 70

                    results.append({
                        "s": s, "p": last_p, "c": change, 
                        "v": volumes[-1], "f": forecast, "conf": conf
                    })
                    print(f"[OK] {s}: {last_p} ({change}%)")
            time.sleep(0.3) # Tránh bị chặn IP
        except Exception as e:
            print(f"[LỖI] {s}: {str(e)}")

    if results:
        final_output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên kế tiếp",
            "stocks": sorted(results, key=lambda x: x['s'])
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        print("Cập nhật thành công!")

if __name__ == "__main__":
    get_market_data()
