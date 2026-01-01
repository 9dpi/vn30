import json
import requests
from datetime import datetime, timedelta
import time

def get_market_data():
    # 30 mã VN30
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    print("--- ĐANG QUÉT DỮ LIỆU LỊCH SỬ 10 PHIÊN ---")
    
    for s in tickers:
        try:
            # Lấy dữ liệu lùi về 15 ngày để chắc chắn bao phủ các ngày nghỉ lễ
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 15) 
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if data and 'c' in data and len(data['c']) >= 2:
                    prices = data['c']
                    volumes = data['v']
                    
                    last_p = prices[-1] # Giá phiên gần nhất có giao dịch
                    prev_p = prices[-2] # Giá phiên trước đó
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    # Thuật toán dự báo dựa trên biến động mạnh (Volatility)
                    forecast = "THEO DÕI"
                    conf = 65
                    if change <= -2.5: 
                        forecast = "MUA"
                        conf = 85
                    elif change >= 3.0: 
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
            time.sleep(0.2)
        except Exception as e:
            print(f"[LỖI] {s}: {str(e)}")

    if results:
        # SẮP XẾP: Mã biến động mạnh nhất lên đầu theo yêu cầu của bạn
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        
        final_output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên kế tiếp",
            "stocks": results
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        print("Cập nhật data.json thành công!")

if __name__ == "__main__":
    get_market_data()
