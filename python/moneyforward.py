"""
マネーフォワード クラウド勤怠 シフト一括更新

CSVで一括更新 用のCSVを生成する
列構成: 従業員番号,苗字,名前,日付,勤怠区分,勤務パターン,開始時刻,終了時刻,休憩x3
"""
import csv
import io
import logging
import os
import tempfile
from playwright.sync_api import sync_playwright, Page
from models import StaffShift

logger = logging.getLogger(__name__)

# 勤怠区分マッピング (シフト記号 → 平日/休日)
WORK_TYPE = {
    '日': '平日',
    '前': '平日',
    '後': '平日',
    'オン': '平日',
    '休オ': '休日',
    '公': '休日',
    '希': '休日',
    '有': '休日',
    '欠': '休日',
    '研': '平日',
    '': None,  # 空白はスキップ
}


def _get_pattern(code: str, mapping: dict) -> str:
    """シフト記号とスタッフマッピングから勤務パターン名を返す"""
    if code == '日':
        return mapping.get('day_pattern', '日勤')
    if code == 'オン':
        return mapping.get('oncall_pattern', mapping.get('day_pattern', '日勤'))
    if code == '前':
        return mapping.get('morning_pattern', '午前')
    if code == '後':
        return mapping.get('afternoon_pattern', '午後')
    if code == '研':
        return mapping.get('day_pattern', '日勤')
    if code == '有':
        return '有給'
    if code == '欠':
        return '欠勤'
    # 公/希/休オ → パターンなし
    return ''


def generate_csv(staff_list: list[StaffShift], staff_mapping: dict) -> str:
    """
    マネーフォワード勤怠「CSVで一括更新」用のCSVを生成する

    列: 従業員番号,苗字,名前,日付,勤怠区分,勤務パターン,
        開始時刻,終了時刻,休憩開始時刻1,休憩終了時刻1,
        休憩開始時刻2,休憩終了時刻2,休憩開始時刻3,休憩終了時刻3
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        '従業員番号', '苗字', '名前', '日付', '勤怠区分', '勤務パターン',
        '開始時刻', '終了時刻',
        '休憩開始時刻1', '休憩終了時刻1',
        '休憩開始時刻2', '休憩終了時刻2',
        '休憩開始時刻3', '休憩終了時刻3',
    ])

    skipped = []
    for staff in staff_list:
        m = staff_mapping.get(staff.furigana)
        if not m:
            skipped.append(staff.name)
            continue

        for day_idx, code in enumerate(staff.shifts):
            work_type = WORK_TYPE.get(code)
            if work_type is None:
                continue  # 空白はスキップ

            day = day_idx + 1
            date_str = f'{staff.year}/{staff.month}/{day}'  # YYYY/M/D
            pattern = _get_pattern(code, m) if work_type == '平日' else ''

            writer.writerow([
                m['employee_id'],
                m['last_name'],
                m['first_name'],
                date_str,
                work_type,
                pattern,
                '', '', '', '', '', '', '', '',
            ])

    if skipped:
        logger.warning(f'マッピング未登録のスタッフ: {", ".join(skipped)}')

    return output.getvalue()


class MoneyForwardAutomator:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self._pw = None
        self._browser = None
        self._page: Page | None = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=False)
        self._page = self._browser.new_page()
        self._login()
        return self

    def __exit__(self, *_):
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def _login(self):
        logger.info(f'マネーフォワード: {self.url} にアクセス')
        self._page.goto(f'{self.url}/session/new')
        # TODO: ログイン処理
        self._page.wait_for_load_state('networkidle')

    def upload_csv(self, csv_content: str, year: int, month: int):
        """「CSVで一括更新」でCSVをアップロード"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                         encoding='utf-8-sig', delete=False) as f:
            f.write(csv_content)
            tmp_path = f.name
        try:
            # TODO: CSVアップロードのセレクタを実装
            raise NotImplementedError('CSVアップロードは手動で実施してください')
        finally:
            os.unlink(tmp_path)
