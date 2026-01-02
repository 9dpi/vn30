import json, requests, time
from datetime import datetime, timedelta

def fetch_from_tcbs(s, start_ts, end_ts):
    url = f"https://apipub.tcbs.com.vn/trading/v1/derivative/candles?ticker={s}&type=stock&resolution=D&from={start_ts}&to={end_ts}"
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
        data = res.json()
        if data and len(data) >= 2:
            ohlc = [{"x": datetime.fromtimestamp(d['t']//1000 if d['t'] > 1e11 else d['t']).strftime('%Y-%m-%d'), 
                     "y": [d['o'], d['h'], d['l'], d['c']]} for d in data]
            return {"p": data[-1]['c'], "c": round(((data[-1]['c'] - data[-2]['c']) / data[-2]['c']) * 100, 2), "v": data[-1]['v'], "chart": ohlc}
    return None

def fetch_from_ssi(s, start_ts, end_ts):
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://iboard.ssi.com.vn/'}
    url = f"https://iboard-query.ssi.com.vn/stock/chart/history?symbol={s}&resolution=D&from={start_ts}&to={end_ts}"
    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code == 200:
        d = res.json()
        if d and d.get('s') == 'ok' and len(d.get('c', [])) >= 2:
            ohlc = [{"x": datetime.fromtimestamp(d['t'][i]).strftime('%Y-%m-%d'), "y": [d['o'][i], d['h'][i], d['l'][i], d['c'][i]]} for i in range(len(d['t']))]
            return {"p": d['c'][-1], "c": round(((d['c'][-1] - d['c'][-2]) / d['c'][-2]) * 100, 2), "v": d['v'][-1], "chart": ohlc}
    return None

def get_market_data():
    tickers = ["ACB","BCM","BID","BVH","CTG","FPT","GAS","GVR","HDB","HPG","MBB","MSN","MWG","PLX","POW","SAB","SHB","SSB","SSI","STB","TCB","TPB","VCB","VHM","VIB","VIC","VNM","VPB","VRE","VJC"]
    results = []
    end_ts = int(time.time())
    start_ts = int((datetime.now() - timedelta(days=30)).timestamp())

    print(f"--- KHỞI CHẠY HỆ THỐNG QUÉT ĐA NGUỒN (FALLBACK MODE) ---")

    for s in tickers:
        data = None
        # Thử nguồn 1: TCBS
        try: data = fetch_from_tcbs(s, start_ts, end_ts)
        except: pass
        
        # Thử nguồn 2 nếu nguồn 1 thất bại: SSI
        if not data:
            try: 
                print(f"[!] {s}: Thử nguồn dự phòng SSI...")
                data = fetch_from_ssi(s, start_ts, end_ts)
            except: pass

        if data:
            results.append({
                "s": s, "p": data['p'], "c": data['c'], "v": data['v'],
                "f": "MUA" if data['c'] < -2.5 else ("BÁN" if data['c'] > 2.5 else "THEO DÕI"),
                "conf": 80 if abs(data['c']) > 2.5 else 65,
                "chart_data": data['chart']
            })
            print(f"[OK] {s}: {data['p']} ({data['c']}%)")
        else:
            print(f"[FAIL] {s}: Tất cả các nguồn đều chặn hoặc lỗi.")
        time.sleep(0.5)

    if results:
        # Tự động sắp xếp theo biến động mạnh nhất lên đầu
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        output = {"update_time": datetime.now().strftime("%H:%M:%S %d/%m/%Y"), "stocks": results}
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print("--- HOÀN TẤT CẬP NHẬT DỮ LIỆU ---")

if __name__ == "__main__":
    get_market_data()
