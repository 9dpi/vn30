import json, requests, time
from datetime import datetime, timedelta

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    
    # DNSE khá thoáng, chỉ cần Header cơ bản này là đủ
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    print(f"--- BẮT ĐẦU LẤY DATA TỪ DNSE - {datetime.now().strftime('%H:%M:%S')} ---")
    
    # Lấy dữ liệu 30 ngày để đảm bảo luôn có phiên gần nhất
    end_ts = int(time.time())
    start_ts = end_ts - (86400 * 30)

    for s in tickers:
        try:
            url = f"https://api.dnse.com.vn/chart/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            res = requests.get(url, headers=headers, timeout=15)
            
            if res.status_code == 200:
                d = res.json()
                # DNSE trả về cấu trúc: { s: 'ok', t: [], o: [], h: [], l: [], c: [], v: [] }
                if d and 'c' in d and len(d['c']) >= 2:
                    ohlc = [{"x": datetime.fromtimestamp(d['t'][i]).strftime('%Y-%m-%d'), 
                             "y": [d['o'][i], d['h'][i], d['l'][i], d['c'][i]]} for i in range(len(d['t']))]
                    
                    last_p, prev_p = d['c'][-1], d['c'][-2]
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    results.append({
                        "s": s, "p": last_p, "c": change, "v": d['v'][-1],
                        "f": "MUA" if change < -2.5 else ("BÁN" if change > 3 else "THEO DÕI"),
                        "conf": 80 if abs(change) > 2.5 else 65,
                        "chart_data": ohlc
                    })
                    print(f"[OK] {s}: {last_p} ({change}%)")
                else:
                    print(f"[TRỐNG] {s}: Không có dữ liệu giao dịch")
            else:
                print(f"[LỖI {res.status_code}] {s}")
            
            time.sleep(0.3) # Nghỉ ngắn để duy trì kết nối ổn định
        except Exception as e:
            print(f"[ERR] {s}: {str(e)}")

    if results:
        # Sắp xếp theo biến động mạnh nhất (trị tuyệt đối) để đẩy mã HOT lên đầu
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        
        output = {
            "update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "forecast_for": "Phiên giao dịch tới",
            "stocks": results
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"--- ĐÃ LƯU THÀNH CÔNG {len(results)} MÃ VÀO DATA.JSON ---")
    else:
        print("--- THẤT BẠI: MẢNG DỮ LIỆU RỖNG ---")

if __name__ == "__main__":
    get_market_data()
