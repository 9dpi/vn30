import json
import requests
from datetime import datetime, timedelta

def get_market_data():
    # Danh sách 30 mã cổ phiếu VN30 (Nhóm hot nhất thị trường)
    tickers = [
        "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
        "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
        "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VNM", "VPB", "VRE", "VJC"
    ]
    
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print(f"--- BẮT ĐẦU CẬP NHẬT {len(tickers)} MÃ ---")
    
    for s in tickers:
        try:
            # Sử dụng API của SSI/Vietstock thông qua nguồn dự phòng ổn định
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={int((datetime.now() - timedelta(days=7)).timestamp())}&to={int(datetime.now().timestamp())}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data_stock = response.json()
                if data_stock and 'c' in data_stock and len(data_stock['c']) >= 2:
                    last_p = data_stock['c'][-1] # Giá đóng cửa gần nhất
                    prev_p = data_stock['c'][-2] # Giá phiên trước
                    change_pc = round(((last_p - prev_p) / prev_p) * 100, 2)
                    vol = data_stock['v'][-1] if 'v' in data_stock else 0

                    # Thuật toán dự báo dựa trên biến động và xu hướng
                    forecast = "THEO DÕI"
                    conf = 65
                    if change_pc < -2.5: 
                        forecast = "MUA"
                        conf = 85
                    elif change_pc > 3.0: 
                        forecast = "BÁN"
                        conf = 80
                    elif -0.5 <= change_pc <= 0.5:
                        forecast = "TÍCH LŨY"
                        conf = 70

                    results.append({
                        "s": s,
                        "p": last_p,
                        "c": change_pc,
                        "v": vol,
                        "f": forecast,
                        "conf": conf
                    })
                    print(f"[OK] {s}: {last_p} ({change_pc}%)")
                else:
                    print(f"[WARN] {s}: Dữ liệu không đủ để tính toán.")
            else:
                print(f"[ERROR] {s}: API trả về lỗi {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {s}: Lỗi kết nối - {str(e)}")

    print(f"--- HOÀN TẤT: LẤY ĐƯỢC {len(results)}/{len(tickers)} MÃ ---")

    # Chỉ cập nhật file nếu lấy được ít nhất 1 mã để tránh làm hỏng Dashboard
    if len(results) > 0:
        output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên kế tiếp",
            "stocks": sorted(results, key=lambda x: x['s'])
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
    else:
        print("[CRITICAL] Không lấy được bất kỳ dữ liệu nào. Giữ nguyên file cũ.")

if __name__ == "__main__":
    get_market_data()
