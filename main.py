import json
import requests
from datetime import datetime, timedelta
import time

def get_vn30_data():
    # Danh sách 30 mã VN30 chuẩn
    tickers = [
        "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
        "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
        "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VNM", "VPB", "VRE", "VJC"
    ]
    
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://google.com'
    }

    print(f"--- BẮT ĐẦU QUÉT DỮ LIỆU {len(tickers)} MÃ ---")
    
    for s in tickers:
        try:
            # Sử dụng API của Vietstock/SSI thông qua lịch sử giá (ổn định hơn bảng điện realtime)
            end_date = int(time.time())
            start_date = end_date - (86400 * 10) # Lấy dữ liệu 10 ngày gần nhất
            
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_date}&to={end_date}"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data and 'c' in data and len(data['c']) >= 2:
                    curr_p = data['c'][-1]  # Giá đóng cửa hôm nay
                    prev_p = data['c'][-2]  # Giá đóng cửa hôm qua
                    change = round(((curr_p - prev_p) / prev_p) * 100, 2)
                    vol = data['v'][-1] if 'v' in data: data['v'][-1] else 0

                    # Thuật toán dự báo AI đơn giản
                    forecast = "THEO DÕI"
                    conf = 60
                    if change <= -2.0:
                        forecast = "MUA"
                        conf = 85
                    elif change >= 2.5:
                        forecast = "BÁN"
                        conf = 80
                    elif -0.5 <= change <= 0.5:
                        forecast = "GIỮ"
                        conf = 75

                    results.append({
                        "s": s, "p": curr_p, "c": change, "v": vol, "f": forecast, "conf": conf
                    })
                    print(f"[OK] {s}: {curr_p} ({change}%)")
                else:
                    print(f"[SKIP] {s}: Không đủ dữ liệu lịch sử")
            else:
                print(f"[FAIL] {s}: API lỗi {response.status_code}")
                
            # Nghỉ ngắn giữa các lần gọi để tránh bị chặn (Rate limit)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"[ERROR] {s}: {str(e)}")

    print(f"--- HOÀN TẤT: LẤY ĐƯỢC {len(results)}/{len(tickers)} MÃ ---")

    # Chỉ ghi file nếu có ít nhất 1 mã để tránh ghi đè file rỗng lên Dashboard
    if len(results) > 0:
        final_data = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"),
            "stocks": sorted(results, key=lambda x: x['s'])
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print("Đã cập nhật data.json thành công!")
    else:
        print("CẢNH BÁO: Không lấy được dữ liệu mới. Giữ nguyên data cũ.")

if __name__ == "__main__":
    get_vn30_data()
