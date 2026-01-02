import json, requests, time
from datetime import datetime, timedelta

def fetch_yahoo(s):
    """Nguồn 1: Yahoo Finance (Uy tín nhất)"""
    symbol = f"{s}.VN"
    end_ts = int(time.time())
    start_ts = int((datetime.now() - timedelta(days=30)).timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={start_ts}&period2={end_ts}&interval=1d"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    if res.status_code == 200:
        data = res.json().get('chart', {}).get('result', [])[0]
        close_p = data.get('indicators', {}).get('adjclose', [])[0].get('adjclose', [])
        if len(close_p) >= 2:
            return {"p": round(close_p[-1], 1), "c": round(((close_p[-1] - close_p[-2]) / close_p[-2]) * 100, 2), "v": data['indicators']['quote'][0]['volume'][-1]}
    return None

def fetch_stooq(s):
    """Nguồn 2: Stooq.com (Dự phòng quốc tế cực tốt)"""
    # Stooq dùng mã định dạng ticker.vn
    url = f"https://stooq.com/q/d/l/?s={s.lower()}.vn&i=d"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    if res.status_code == 200 and "Date" in res.text:
        lines = res.text.strip().split('\n')
        if len(lines) >= 3:
            last_row = lines[-1].split(',')
            prev_row = lines[-2].split(',')
            last_p, prev_p = float(last_row[4]), float(prev_row[4])
            return {"p": last_p, "c": round(((last_p - prev_p) / prev_p) * 100, 2), "v": int(last_row[5])}
    return None

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    
    print("--- HỆ THỐNG DỰ PHÒNG QUỐC TẾ: YAHOO -> STOOQ ---")

    for s in tickers:
        # Thử Yahoo trước
        data = fetch_yahoo(s)
        
        # Nếu Yahoo lỗi, tự động chuyển sang Stooq
        if not data:
            print(f"[!] {s}: Yahoo lỗi, đang chuyển sang Stooq...")
            try: data = fetch_stooq(s)
            except: data = None

        if data:
            results.append({
                "s": s, "p": data['p'], "c": data['c'], "v": data['v'],
                "f": "MUA" if data['c'] < -2.5 else ("BÁN" if data['c'] > 3 else "THEO DÕI"),
                "conf": 80 if abs(data['c']) > 2.5 else 65
            })
            print(f"[OK] {s}: {data['p']} ({data['c']}%)")
        else:
            print(f"[FAIL] {s}: Tất cả nguồn quốc tế đều không phản hồi.")
        time.sleep(0.5)

    if results:
        # Sắp xếp theo biến động mạnh nhất lên đầu
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        output = {"update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"), "stocks": results}
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"--- THÀNH CÔNG: ĐÃ CẬP NHẬT {len(results)} MÃ ---")

if __name__ == "__main__":
    get_market_data()
