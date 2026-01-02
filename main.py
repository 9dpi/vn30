import json
import requests
from datetime import datetime, timedelta
import time

def get_market_data():
    # Danh sách mã VN30 (Khai báo ban đầu để quản lý)
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://iboard.ssi.com.vn/'
    }

    print("--- BẮT ĐẦU TRÍCH XUẤT DỮ LIỆU ---")
    
    # Lấy dữ liệu 30 ngày để đảm bảo luôn có phiên giao dịch gần nhất
    end_ts = int(time.time())
    start_ts = int((datetime.now() - timedelta(days=30)).timestamp())

    for s in tickers:
        try:
            # Sử dụng API SSI iBoard (Dữ liệu nến ngày)
            url = f"https://iboard-query.ssi.com.vn/stock/chart/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            res = requests.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                data = res.json()
                # Kiểm tra cấu trúc dữ liệu trả về từ SSI (t, o, h, l, c, v)
                if data and data.get('s') == 'ok' and 'c' in data and len(data['c']) >= 2:
                    
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
                    
                    results.append({
                        "s": s, 
                        "p": last_p, 
                        "c": change, 
                        "v": data['v'][-1], 
                        "f": "MUA" if change < -2.5 else ("BÁN" if change > 3 else "THEO DÕI"),
                        "conf": 80 if abs(change) > 2.5 else 65,
                        "chart_data": ohlc_data 
                    })
                    print(f"[OK] {s}: {last_p} ({change}%)")
                else:
                    print(f"[TRỐNG] {s}: Không có dữ liệu.")
            else:
                print(f"[LỖI {res.status_code}] {s}")
            
            time.sleep(0.5) # Tránh bị giới hạn tần suất gửi yêu cầu
            
        except Exception as e:
            print(f"[ERR] {s}: {str(e)}")

    if results:
        # LOGIC QUAN TRỌNG: Sắp xếp theo biến động (c) mạnh nhất lên đầu
        # Sử dụng abs(x['c']) để lấy giá trị tuyệt đối (tăng mạnh nhất hoặc giảm mạnh nhất)
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        
        final_output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên giao dịch tới",
            "stocks": results
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        print("--- ĐÃ LƯU VÀ SẮP XẾP DỮ LIỆU THÀNH CÔNG ---")
    else:
        print("--- THẤT BẠI: DỮ LIỆU RỖNG ---")

if __name__ == "__main__":
    get_market_data()
