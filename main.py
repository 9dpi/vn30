import json
import requests
from datetime import datetime, timedelta
import time

def get_market_data():
    # Danh sách 30 mã VN30 chuẩn
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    
    # Giả lập trình duyệt để tránh bị các API tài chính chặn kết nối
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://vietstock.vn/'
    }

    print("--- BẮT ĐẦU QUÉT DỮ LIỆU LỊCH SỬ 30 PHIÊN ---")
    
    for s in tickers:
        try:
            # Lấy dữ liệu 30 ngày để đảm bảo luôn có data kể cả ngày lễ và đủ vẽ biểu đồ nến
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 30) 
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                # Kiểm tra nếu có dữ liệu giá đóng cửa (c) và ít nhất 2 phiên để tính biến động
                if data and 'c' in data and len(data['c']) >= 2:
                    
                    # Chuẩn bị dữ liệu OHLC cho biểu đồ nến trên Website
                    ohlc_data = []
                    for i in range(len(data['t'])):
                        ohlc_data.append({
                            "x": datetime.fromtimestamp(data['t'][i]).strftime('%Y-%m-%d'),
                            "y": [data['o'][i], data['h'][i], data['l'][i], data['c'][i]]
                        })
                    
                    last_p = data['c'][-1] # Giá đóng cửa phiên gần nhất
                    prev_p = data['c'][-2] # Giá đóng cửa phiên trước đó
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    # Thuật toán dự báo dựa trên biến động giá
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
                    print(f"[TRỐNG] {s}: API không trả về dữ liệu nến.")
            else:
                print(f"[LỖI KẾT NỐI] {s}: HTTP {res.status_code}")
                
            # Nghỉ ngắn giữa các mã để tránh bị khóa IP do gửi yêu cầu quá nhanh
            time.sleep(0.4) 
            
        except Exception as e:
            print(f"[LỖI HỆ THỐNG] {s}: {str(e)}")

    if results:
        # SẮP XẾP: Đưa các mã có biến động tuyệt đối mạnh nhất lên đầu bảng
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
        print("--- THẤT BẠI: KHÔNG CÓ DỮ LIỆU ĐỂ LƯU ---")

if __name__ == "__main__":
    get_market_data()
