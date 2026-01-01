import json, requests, time
from datetime import datetime, timedelta

def get_market_data():
    # 30 mã VN30 chuẩn
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    # Giả lập trình duyệt để tránh bị chặn
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://vietstock.vn/'
    }

    print("--- BẮT ĐẦU QUÉT DỮ LIỆU LỊCH SỬ (15 NGÀY) ---")
    
    for s in tickers:
        try:
            # Lấy 15 ngày để chắc chắn bao phủ ngày nghỉ 01/01
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 15)
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                d = res.json()
                if d and 'c' in d and len(d['c']) >= 2:
                    # Lấy giá trị phiên gần nhất có dữ liệu
                    last_p, prev_p = d['c'][-1], d['c'][-2]
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    # Chuẩn bị dữ liệu nến cho biểu đồ
                    ohlc = [{"x": datetime.fromtimestamp(d['t'][i]).strftime('%Y-%m-%d'), 
                             "y": [d['o'][i], d['h'][i], d['l'][i], d['c'][i]]} for i in range(len(d['t']))]

                    results.append({
                        "s": s, "p": last_p, "c": change, "v": d['v'][-1],
                        "f": "MUA" if change < -2 else ("BÁN" if change > 2 else "THEO DÕI"),
                        "conf": 80 if abs(change) > 2 else 60,
                        "chart_data": ohlc
                    })
                    print(f"[OK] {s}: {last_p} ({change}%)")
            time.sleep(0.5) # Nghỉ để không bị khóa IP
        except Exception as e:
            print(f"[LỖI] {s}: {e}")

    if results:
        # SẮP XẾP THEO BIẾN ĐỘNG MẠNH NHẤT LÊN ĐẦU
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        
        output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên giao dịch tới",
            "stocks": results
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("--- ĐÃ LƯU DỮ LIỆU THÀNH CÔNG ---")

if __name__ == "__main__":
    get_market_data()
