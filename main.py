import json, requests, time
from datetime import datetime, timedelta

def fetch_yahoo(s):
    symbol = f"{s}.VN"
    end_ts = int(time.time())
    start_ts = int((datetime.now() - timedelta(days=30)).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"
    
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        if res.status_code == 200:
            data = res.json().get('chart', {}).get('result', [])[0]
            # Lấy danh sách giá đóng cửa và lọc bỏ các giá trị None
            raw_close = data.get('indicators', {}).get('adjclose', [])[0].get('adjclose', [])
            close_p = [p for p in raw_close if p is not None]
            
            if len(close_p) >= 2:
                last_p = close_p[-1]
                prev_p = close_p[-2]
                change = round(((last_p - prev_p) / prev_p) * 100, 2)
                
                # Lấy khối lượng phiên cuối (lọc None)
                v_list = [v for v in data['indicators']['quote'][0].get('volume', []) if v is not None]
                volume = v_list[-1] if v_list else 0
                
                return {"p": round(last_p, 1), "c": change, "v": volume}
    except Exception: pass
    return None

def fetch_stooq(s):
    url = f"https://stooq.com/q/d/l/?s={s.lower()}.vn&i=d"
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if res.status_code == 200 and "Date" in res.text:
            lines = res.text.strip().split('\n')
            if len(lines) >= 3:
                last_row = lines[-1].split(',')
                prev_row = lines[-2].split(',')
                last_p, prev_p = float(last_row[4]), float(prev_row[4])
                return {"p": last_p, "c": round(((last_p - prev_p) / prev_p) * 100, 2), "v": int(last_row[5])}
    except Exception: pass
    return None

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    print("--- HỆ THỐNG DỰ PHÒNG QUỐC TẾ: YAHOO -> STOOQ ---")

    for s in tickers:
        data = fetch_yahoo(s)
        if not data:
            print(f"[!] {s}: Yahoo lỗi/rỗng, thử Stooq...")
            data = fetch_stooq(s)

        if data:
            results.append({
                "s": s, "p": data['p'], "c": data['c'], "v": data['v'],
                "f": "MUA" if data['c'] < -2.0 else ("BÁN" if data['c'] > 2.0 else "THEO DÕI"),
                "conf": 80 if abs(data['c']) > 2.0 else 65
            })
            print(f"[OK] {s}: {data['p']} ({data['c']}%)")
        else:
            print(f"[FAIL] {s}: Không có dữ liệu.")
        time.sleep(0.5)

    if results:
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        output = {"update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"), "stocks": results}
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"--- THÀNH CÔNG: ĐÃ CẬP NHẬT {len(results)} MÃ ---")

if __name__ == "__main__":
    get_market_data()
