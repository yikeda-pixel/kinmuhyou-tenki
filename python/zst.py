"""
ZST (homecare.zest.jp) シフトカレンダーへの自動入力

TODO: 実際の HTML を確認してセレクタを実装してください
ブラウザの開発者ツール(F12) → Elements タブで要素を確認できます
"""
import logging
from playwright.sync_api import sync_playwright, Page
from models import StaffShift
from shift_mapper import ZST_MAP

logger = logging.getLogger(__name__)


class ZSTAutomator:
    def __init__(self, url: str, username: str, password: str):
        self.url = url   # 例: https://homecare.zest.jp/office/.../calendar/shift
        self.username = username
        self.password = password
        self._pw = None
        self._browser = None
        self._page: Page | None = None

    def __enter__(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=False)  # 確認のため画面表示
        self._page = self._browser.new_page()
        self._open_calendar()
        return self

    def __exit__(self, *_):
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def _open_calendar(self):
        logger.info(f'ZST: {self.url} を開きます')
        self._page.goto(self.url)
        self._page.wait_for_load_state('networkidle')
        logger.info('ZST: カレンダー読み込み完了')
        # ZST はセッション認証済みのURLを直接開く想定
        # もしログイン画面にリダイレクトされる場合は以下を有効化:
        # if 'login' in self._page.url or 'signin' in self._page.url:
        #     self._page.fill('input[type="email"]', self.username)
        #     self._page.fill('input[type="password"]', self.password)
        #     self._page.click('button[type="submit"]')
        #     self._page.wait_for_url('**/calendar/**')

    def input_staff_shifts(self, staff: StaffShift) -> int:
        """1名分の全シフトを入力し、成功した件数を返す"""
        success = 0
        for day_idx, code in enumerate(staff.shifts):
            day = day_idx + 1
            if not code or code not in ZST_MAP:
                continue
            try:
                self._set_one_shift(staff.name, day, code)
                success += 1
            except NotImplementedError:
                raise
            except Exception as e:
                logger.error(f'ZST: {staff.name} {day}日 ({code}) 失敗 - {e}')
        return success

    def _set_one_shift(self, staff_name: str, day: int, code: str):
        zst = ZST_MAP[code]
        logger.info(f'ZST: {staff_name} {day}日 → {zst.shift_type}{"(オンコール)" if zst.oncall else ""}')

        # ==============================================================
        # TODO: 以下のセレクタを ZST の実際の HTML に合わせて実装してください
        #
        # ① スタッフ名の行を探す
        #    row = self._page.locator('tr').filter(has_text=staff_name).first
        #
        # ② その行の n 列目（日付列）のセルをクリック
        #    cell = row.locator('td').nth(day + 2)  # オフセットは要確認
        #    cell.click()
        #
        # ③ 右パネルが開いたらシフトタイプを選択
        #    self._page.wait_for_selector('.shift-panel', state='visible')
        #    self._page.click(f'button:has-text("{zst.shift_type}")')
        #
        # ④ オンコールの場合は追加でオンコールフラグをON
        #    if zst.oncall:
        #        self._page.click('.oncall-toggle')
        #
        # ⑤ 保存
        #    self._page.click('button:has-text("保存")')
        #    self._page.wait_for_timeout(300)
        # ==============================================================

        raise NotImplementedError(
            'ZST のセレクタを実装してください (python/zst.py の _set_one_shift メソッド)\n'
            'ブラウザの F12 → Elements タブでセレクタを確認できます'
        )
