import json, requests, time
from datetime import datetime, timedelta

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for s in tickers:
        try:
            # Lấy 30 ngày để có đủ dữ liệu vẽ nến
            end_ts = int(time.time())
            start_ts = end_ts - (86400 * 30)
            url = f"https://api.vietstock.vn/ta/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                d = res.json()
                if d and 'c' in d and len(d['c']) >= 2:
                    # Dữ liệu nến cho ApexCharts
                    ohlc = [{"x": datetime.fromtimestamp(d['t'][i]).strftime('%Y-%m-%d'), 
                             "y": [d['o'][i], d['h'][i], d['l'][i], d['c'][i]]} for i in range(len(d['t']))]
                    
                    last_p, prev_p = d['c'][-1], d['c'][-2]
                    change = round(((last_p - prev_p) / prev_p) * 100, 2)
                    
                    # Thuật toán dự báo đơn giản
                    f, conf = "THEO DÕI", 65
                    if change <= -2.0: f, conf = "MUA", 85
                    elif change >= 2.0: f, conf = "BÁN", 80

                    results.append({"s": s, "p": last_p, "c": change, "v": d['v'][-1], "f": f, "conf": conf, "chart_data": ohlc})
            time.sleep(0.2)
        except: continue

    if results:
        # SẮP XẾP THEO BIẾN ĐỘNG MẠNH NHẤT (Giá trị tuyệt đối)
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump({"update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"), 
                       "forecast_for": "Phiên tới", "stocks": results}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_market_data()
