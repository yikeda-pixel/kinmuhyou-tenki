"""
マネーフォワード クラウド勤怠 シフト一括更新

戦略: 「CSVで一括更新」ボタンを使う（手動操作より確実）
1. Python が CSV ファイルを生成
2. Playwright が「CSVで一括更新」ボタンを押してファイルをアップロード

CSV フォーマットについて:
  マネーフォワード管理画面 → シフト管理 → 「エクスポート履歴」でサンプルCSVを
  ダウンロードし、実際のフォーマットを確認してください
  確認後 generate_csv() のヘッダー・列を修正してください
"""
import csv
import io
import logging
import tempfile
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
from models import StaffShift
from shift_mapper import MF_MAP

logger = logging.getLogger(__name__)


def generate_csv(staff_list: list[StaffShift]) -> str:
    """
    マネーフォワード勤怠「CSVで一括更新」用のCSVを生成する

    NOTE: 実際のフォーマットを以下の手順で確認してください:
      1. マネーフォワード → シフト管理 → 「エクスポート履歴」
      2. サンプルCSVをダウンロード
      3. 列名をこの関数のヘッダーに合わせて修正
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # TODO: マネーフォワードの実際のCSVヘッダーに合わせて変更
    writer.writerow(['氏名', '年月日', 'スケジュール', '開始時刻', '終了時刻', '勤務区分'])

    for staff in staff_list:
        for day_idx, code in enumerate(staff.shifts):
            if not code or code not in MF_MAP:
                continue
            mf = MF_MAP[code]
            day = day_idx + 1
            date_str = f'{staff.year}/{staff.month:02d}/{day:02d}'

            writer.writerow([
                staff.name,
                date_str,
                mf.pattern or '',
                mf.start or '',
                mf.end or '',
                mf.day_type,
            ])

    return output.getvalue()


class MoneyForwardAutomator:
    def __init__(self, url: str, username: str, password: str):
        self.url = url  # 例: https://attendance.moneyforward.com
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
        login_url = f'{self.url}/session/new'
        logger.info(f'マネーフォワード: {login_url} にアクセス')
        self._page.goto(login_url)
        # TODO: ログイン処理
        # self._page.fill('input[name="email"]', self.username)
        # self._page.click('input[type="submit"]')
        # self._page.fill('input[name="password"]', self.password)
        # self._page.click('input[type="submit"]')
        # self._page.wait_for_url('**/attendance**')
        self._page.wait_for_load_state('networkidle')
        logger.info('マネーフォワード: 読み込み完了')

    def upload_csv(self, csv_content: str, year: int, month: int):
        """「CSVで一括更新」ボタンを押してCSVをアップロード"""
        # CSVを一時ファイルに保存
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                         encoding='utf-8-sig', delete=False) as f:
            f.write(csv_content)
            tmp_path = f.name

        try:
            shift_url = f'{self.url}/admin/shift_management/pattern_shift_schedules'
            logger.info(f'マネーフォワード: {shift_url} へ移動')
            self._page.goto(shift_url)
            self._page.wait_for_load_state('networkidle')

            # ==============================================================
            # TODO: 以下のセレクタをマネーフォワードの実際のHTMLに合わせて実装
            #
            # ① 年月を設定 (必要な場合)
            #    self._page.select_option('select[name="year"]', str(year))
            #    self._page.select_option('select[name="month"]', str(month))
            #    self._page.click('button:has-text("検索")')
            #
            # ② 「CSVで一括更新」ボタンをクリック
            #    self._page.click('a:has-text("CSVで一括更新")')
            #
            # ③ ファイル選択ダイアログにCSVをセット
            #    with self._page.expect_file_chooser() as fc_info:
            #        self._page.click('input[type="file"]')
            #    fc_info.value.set_files(tmp_path)
            #
            # ④ アップロード実行
            #    self._page.click('button:has-text("更新する")')
            #    self._page.wait_for_selector('.success-message')
            # ==============================================================

            raise NotImplementedError(
                'マネーフォワードのCSVアップロードセレクタを実装してください '
                '(python/moneyforward.py の upload_csv メソッド)'
            )
        finally:
            os.unlink(tmp_path)
