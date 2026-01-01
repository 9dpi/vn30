import json
import requests
from datetime import datetime, timedelta

def get_vn30_data():
    # Danh sách mã VN30
    tickers = ["FPT", "VCB", "VIC", "VNM", "HPG", "MBB", "MWG", "STB", "TCB", "VHM", "GAS", "BID", "ACB", "PLX", "POW"]
    
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    print("Đang lấy dữ liệu từ nguồn dự phòng...")
    
    for s in tickers:
        try:
            # Sử dụng API của CafeF hoặc SSI (thay đổi endpoint để tránh bị chặn)
            url = f"https://msh.com.vn/Handlers/StockHandler.ashx?do=getshdata&symbol={s}"
            response = requests.get(url, headers=headers, timeout=10)
            item = response.json()[0]
            
            price = float(item['LastPrice'])
            change_pc = float(item['ChangePercent'])
            volume = int(item['TotalVolume'])

            # Logic dự báo đơn giản dựa trên kỹ thuật
            forecast = "THEO DÕI"
            if change_pc < -2.0: forecast = "MUA"
            elif change_pc > 2.5: forecast = "BÁN"
            else: forecast = "GIỮ"

            results.append({
                "s": s,
                "p": price,
                "c": round(change_pc, 2),
                "v": volume,
                "f": forecast,
                "conf": 70
            })
            print(f"Thành công: {s}")
        except Exception as e:
            print(f"Lỗi mã {s}: {e}")

    # Đóng gói dữ liệu
    data = {
        "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
        "forecast_for": (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"),
        "stocks": sorted(results, key=lambda x: x['c'], reverse=True)
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_vn30_data()
