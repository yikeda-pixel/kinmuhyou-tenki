"""
スプレッドシートのシフト記号 → ZST / マネーフォワード勤怠 へのマッピング
TODO が付いている箇所は実際の画面を確認して調整してください
"""
from dataclasses import dataclass
from typing import Optional


# 記号 → 日本語表示名
SHIFT_LABEL: dict[str, str] = {
    '日':   '日勤',
    '前':   '午前',
    '後':   '午後',
    'オン': 'オンコール',
    '休オ': '休みオンコール',
    '公':   '公休',
    '希':   '希望休',
    '有':   '有給',
    '欠':   '欠勤',
    '研':   '研修',
    '':     '－',
}

# 色 (フロントエンド表示用)
SHIFT_COLOR: dict[str, str] = {
    '日':   '#4299e1',  # 青
    '前':   '#48bb78',  # 緑
    '後':   '#ed8936',  # オレンジ
    'オン': '#9f7aea',  # 紫
    '休オ': '#b794f4',  # 薄紫
    '公':   '#a0aec0',  # グレー
    '希':   '#f6ad55',  # 黄
    '有':   '#68d391',  # 薄緑
    '欠':   '#fc8181',  # 赤
    '研':   '#76e4f7',  # 水色
    '':     '#edf2f7',  # 白
}

# =============================================
# ZST 用マッピング
# =============================================

@dataclass
class ZSTShift:
    shift_type: str   # 常勤 / AM / 公休 / 希年 / 欠勤 など
    oncall: bool = False

ZST_MAP: dict[str, ZSTShift] = {
    '日':   ZSTShift('常勤'),
    '前':   ZSTShift('AM'),
    '後':   ZSTShift('常勤'),       # TODO: ZSTに午後タイプがあれば名称を変更
    'オン': ZSTShift('常勤', oncall=True),
    '休オ': ZSTShift('公休', oncall=True),
    '公':   ZSTShift('公休'),
    '希':   ZSTShift('希年'),
    '有':   ZSTShift('希年'),       # TODO: ZSTの有給タイプ名を確認
    '欠':   ZSTShift('欠勤'),
    '研':   ZSTShift('常勤'),       # TODO: ZSTに研修タイプがあれば変更
}

# =============================================
# マネーフォワード勤怠 用マッピング
# =============================================

@dataclass
class MFShift:
    day_type: str                   # 平日 / 休日
    pattern: Optional[str] = None  # スケジュール名: 日勤 / 午前 / 午後 / 有給 / 欠勤
    start: Optional[str] = None    # 開始時刻 HH:MM
    end: Optional[str] = None      # 終了時刻 HH:MM

MF_MAP: dict[str, MFShift] = {
    '日':   MFShift('平日', '日勤', '08:30', '17:30'),
    '前':   MFShift('平日', '午前', '08:30', '12:30'),
    '後':   MFShift('平日', '午後', '13:30', '17:30'),
    'オン': MFShift('平日', '日勤', '08:30', '17:30'),  # オンコールは日勤扱い
    '休オ': MFShift('休日'),
    '公':   MFShift('休日'),
    '希':   MFShift('休日'),
    '有':   MFShift('休日', '有給'),
    '欠':   MFShift('休日', '欠勤'),
    '研':   MFShift('平日', '日勤', '08:30', '17:30'),
}
