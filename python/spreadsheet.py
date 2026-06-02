import requests
from datetime import datetime
from models import ShiftRecord

SAMPLE_DATA = [
    {"スタッフ名": "田中太郎", "日付": "2024/12/01", "出勤時間": "09:00", "退勤時間": "18:00", "休憩(分)": 60, "備考": ""},
    {"スタッフ名": "山田花子", "日付": "2024/12/01", "出勤時間": "10:00", "退勤時間": "19:00", "休憩(分)": 60, "備考": ""},
    {"スタッフ名": "佐藤次郎", "日付": "2024/12/02", "出勤時間": "08:30", "退勤時間": "17:30", "休憩(分)": 60, "備考": "早番"},
]


def _parse_record(row: dict) -> ShiftRecord:
    return ShiftRecord(
        staff_name=str(row["スタッフ名"]),
        date=datetime.strptime(str(row["日付"]), "%Y/%m/%d").date(),
        start_time=datetime.strptime(str(row["出勤時間"]), "%H:%M").time(),
        end_time=datetime.strptime(str(row["退勤時間"]), "%H:%M").time(),
        break_minutes=int(row["休憩(分)"]),
        note=str(row.get("備考", "")),
    )


def fetch_from_gas(endpoint_url: str) -> list[ShiftRecord]:
    response = requests.get(endpoint_url, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise ValueError(f"GAS エラー: {data}")
    return [_parse_record(row) for row in data["data"]]


def load_sample_data() -> list[ShiftRecord]:
    return [_parse_record(row) for row in SAMPLE_DATA]
