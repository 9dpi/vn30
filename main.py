import json
from datetime import datetime

data = {
    "update_time": datetime.now().strftime("%H:%M:%S"),
    "forecast_for": "01/01/2026",
    "stocks": [
        {"s": "FPT", "p": 100.0, "c": 1.5, "f": "MUA", "conf": 80}
    ]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Test thành công!")
