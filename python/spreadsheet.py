import requests
from models import StaffShift

# 動作確認用サンプルデータ (実際のスプレッドシートの一部)
SAMPLE_DATA = [
    {
        'name': '池田優(代表）', 'furigana': 'イケダユウ', 'year': 2026, 'month': 6,
        'shifts': ['日','日','日','日','日','公','公','日','日','日','日','日','公','公','日','日','日','日','日','公','公','日','日','日','日','日','公','公','日','日'],
    },
    {
        'name': '才野沙央里', 'furigana': 'サイノサオリ', 'year': 2026, 'month': 6,
        'shifts': ['日','公','日','日','日','公','公','オン','日','日','日','日','公','公','オン','日','日','日','日','公','公','オン','日','日','日','日','公','公','オン','日'],
    },
    {
        'name': '川嶋晏菜', 'furigana': 'カワシマアンナ', 'year': 2026, 'month': 6,
        'shifts': ['オン','日','公','日','オン','日','希','公','日','オン','日','オン','日','希','公','日','日','公','公','オン','オン','日','日','日','公','希','オン','オン','日','日'],
    },
    {
        'name': '財部美希', 'furigana': 'タカラベミキ', 'year': 2026, 'month': 6,
        'shifts': ['日','日','日','日','公','公','公','日','日','日','日','日','公','公','日','日','日','日','日','公','公','日','日','日','日','日','公','公','日','日'],
    },
    {
        'name': '大畑絵璃菜', 'furigana': 'オオハタエリナ', 'year': 2026, 'month': 6,
        'shifts': ['日','日','日','日','日','公','公','前','日','日','日','日','公','公','日','日','日','日','日','公','公','日','日','日','日','日','公','公','日','日'],
    },
]


def _parse(row: dict) -> StaffShift:
    return StaffShift(
        name=row['name'],
        furigana=row['furigana'],
        year=int(row['year']),
        month=int(row['month']),
        shifts=list(row['shifts']),
    )


def fetch_from_gas(endpoint_url: str) -> list[StaffShift]:
    res = requests.get(endpoint_url, timeout=30)
    res.raise_for_status()
    body = res.json()
    if not body.get('success'):
        raise ValueError(f'GAS エラー: {body}')
    return [_parse(r) for r in body['data']]


def load_sample_data() -> list[StaffShift]:
    return [_parse(r) for r in SAMPLE_DATA]
