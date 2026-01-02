# ... (Giữ nguyên các hàm fetch_yahoo của bản Yahoo Finance)

    if results:
        results.sort(key=lambda x: abs(x['c']), reverse=True)
        now = datetime.now()
        
        # Logic tính ngày phiên kế tiếp
        f_date = now + timedelta(days=1)
        while f_date.weekday() >= 5: f_date += timedelta(days=1)

        output = {
            "update_time": now.strftime("%H:%M - %d/%m/%Y"),
            "forecast_for": f_date.strftime("%d/%m/%Y"),
            "next_update": "15:05 Ngày làm việc kế tiếp",
            "stocks": results
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
