import json
import requests
from datetime import datetime, timedelta

def get_vn30_data():
    # Danh sách các mã VN30 (Bạn có thể thêm đủ 30 mã vào đây)
    tickers = ["FPT", "VCB", "VIC", "VNM", "HPG", "MBB", "MWG", "STB", "TCB", "VHM", "GAS", "BID"]
    
    # URL API lấy giá (Ví dụ từ VNDirect)
    url = f"https://finfo-api.vndirect.com.vn/v4/stock_prices?sort=date&filter=code:{','.join(tickers)}&limit={len(tickers)}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    raw_data = response.json()['data']
    
    stock_results = []
    for item in raw_data:
        # Tính toán dự báo đơn giản: 
        # Nếu giá đóng cửa hôm nay thấp hơn hôm qua -> Dự báo Hồi phục (MUA)
        # Nếu tăng quá nóng -> Dự báo Điều chỉnh (BÁN)
        change = round(((item['adClose'] - item['adPriorClose']) / item['adPriorClose']) * 100, 2)
        
        forecast = "THEO DÕI"
        if change < -1.5: forecast = "MUA"
        elif change > 2.0: forecast = "BÁN"
        else: forecast = "GIỮ"

        stock_results.append({
            "s": item['code'],
            "p": item['adClose'],
            "c": change,
            "v": item['nmVolume'],
            "f": forecast,
            "conf": 75 # Độ tin cậy giả định
        })

    # Cấu trúc JSON chuẩn cho Dashboard
    data = {
        "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
        "forecast_for": (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"),
        "stocks": sorted(stock_results, key=lambda x: x['c'], reverse=True)
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_vn30_data()
