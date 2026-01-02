import json
import requests
from datetime import datetime, timedelta
import time

def get_market_data():
    # Danh sách 30 mã VN30
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    
    # Header để giả lập trình duyệt, tránh bị SSI chặn
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://iboard.ssi.com.vn/'
    }

    print("--- BẮT ĐẦU QUÉT DỮ LIỆU TỪ SSI (LẤY 30 NGÀY LỊCH SỬ) ---")
    
    # Tính toán mốc thời gian: từ 30 ngày trước đến hiện tại
    end_ts = int(time.time())
    start_ts = int((datetime.now() - timedelta(days=30)).timestamp())

    for s in tickers:
        try:
            # API SSI iBoard cho dữ liệu nến (History)
            url = f"https://iboard-query.ssi.com.vn/stock/chart/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = requests.get(url, headers=headers, timeout=15)
            
            # Kiểm tra nếu phản hồi thành công
            if res.status_code == 200:
                data = res.json()
                
                # Kiểm tra cấu trúc dữ liệu trả về (SSI trả về các mảng t, o, h, l, c, v)
                if data and isinstance(data, dict) and 'c' in data and len(data['c']) >= 2:
                    
                    # Chuẩn bị dữ liệu OHLC cho biểu đồ nến
                    ohlc_data = []
                    for i in range(len(data['t'])):
                        ohlc_data.append({
                            "x": datetime.fromtimestamp(data['t'][i]).strftime('%Y-%m-%d'),
                            "y": [data['o'][i], data['h'][i], data['l'][i], data['c'][i]]
                        })
                    
                    last_p = data['c'][-1] # Giá đóng cửa phiên gần nhất
                    prev_p = data['c'][-2] # Giá đóng cửa phiên trước đó
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    # Thuật toán dự báo đơn giản
                    forecast = "THEO DÕI"
                    conf = 65
                    if change <= -2.5: forecast, conf = "MUA", 85
                    elif change >= 3.0: forecast, conf = "BÁN", 80

                    results.append({
                        "s": s, 
                        "p": last_p, 
                        "c": change, 
                        "v": data['v'][-1], 
                        "f": forecast, 
                        "conf": conf,
                        "chart_data": ohlc_data 
                    })
                    print(f"[OK] {s}: {last_p} ({change}%)")
                else:
                    print(f"[TRỐNG] {s}: Không có dữ liệu giao dịch.")
            else:
                print(f"[LỖI HTTP] {s}: {res.status_code}")
                
            # Nghỉ ngắn để không bị SSI chặn IP
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[LỖI HỆ THỐNG] {s}: {str(e)}")

    if results:
        # SẮP XẾP: Đưa các mã biến động mạnh nhất (tăng/giảm) lên đầu
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        
        final_output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên giao dịch kế tiếp",
            "stocks": results
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        print("--- CẬP NHẬT DATA.JSON THÀNH CÔNG ---")
    else:
        print("--- THẤT BẠI: KHÔNG LẤY ĐƯỢC DỮ LIỆU NÀO ---")

if __name__ == "__main__":
    get_market_data()
