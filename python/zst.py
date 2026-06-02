import logging
from playwright.sync_api import sync_playwright, Page
from models import ShiftRecord

logger = logging.getLogger(__name__)


class ZSTAutomator:
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
        logger.info(f"ZST: {self.url} にアクセス")
        self._page.goto(self.url)
        # TODO: ZST のログイン画面に合わせてセレクタを設定
        # self._page.fill('#login_id', self.username)
        # self._page.fill('#password', self.password)
        # self._page.click('button[type="submit"]')
        # self._page.wait_for_url('**/dashboard**')
        logger.info("ZST: ログイン (TODO: セレクタを設定してください)")

    def input_shift(self, record: ShiftRecord):
        logger.info(
            f"ZST: 転記 {record.staff_name} {record.date} "
            f"{record.start_time.strftime('%H:%M')}〜{record.end_time.strftime('%H:%M')}"
        )
        # TODO: ZST のシフト入力画面に合わせて実装
        # 例:
        #   self._page.goto(f"{self.url}/shift/{record.date}")
        #   row = self._page.locator(f'tr:has-text("{record.staff_name}")')
        #   row.locator('.start-time').fill(record.start_time.strftime('%H:%M'))
        #   row.locator('.end-time').fill(record.end_time.strftime('%H:%M'))
        #   self._page.click('button#save')
