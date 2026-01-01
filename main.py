import json
import requests
from datetime import datetime, timedelta
import time

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    print("--- ĐANG QUÉT DỮ LIỆU OHLC CHO BIỂU ĐỒ NẾN ---")
    
    for s in tickers:
        try:
            # Lấy dữ liệu 30 ngày để vẽ biểu đồ nến 1 tháng
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 30) # 30 ngày
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if data and 'c' in data and len(data['c']) >= 2:
                    
                    # Chuẩn bị dữ liệu cho biểu đồ nến
                    ohlc_data = []
                    for i in range(len(data['t'])):
                        ohlc_data.append({
                            "x": datetime.fromtimestamp(data['t'][i]).strftime('%Y-%m-%d'),
                            "y": [data['o'][i], data['h'][i], data['l'][i], data['c'][i]]
                        })
                    
                    last_p = data['c'][-1] # Giá đóng cửa phiên gần nhất
                    prev_p = data['c'][-2] # Giá đóng cửa phiên trước đó
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    # Thuật toán dự báo dựa trên biến động giá (Volatility)
                    forecast = "THEO DÕI"
                    conf = 65
                    if change <= -2.5: forecast, conf = "MUA", 85
                    elif change >= 3.0: forecast, conf = "BÁN", 80
                    elif abs(change) < 0.5: forecast, conf = "GIỮ", 70

                    results.append({
                        "s": s, 
                        "p": last_p, 
                        "c": change, 
                        "v": data['v'][-1], 
                        "f": forecast, 
                        "conf": conf,
                        "chart_data": ohlc_data # Thêm dữ liệu biểu đồ vào đây
                    })
            time.sleep(0.2)
        except Exception as e:
            print(f"[LỖI] {s}: {str(e)}")

    if results:
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        final_output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên giao dịch kế tiếp",
            "stocks": results
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        print("Cập nhật data.json thành công!")

if __name__ == "__main__":
    get_market_data()
