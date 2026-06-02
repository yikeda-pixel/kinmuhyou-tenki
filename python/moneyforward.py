import logging
from playwright.sync_api import sync_playwright, Page
from models import ShiftRecord

logger = logging.getLogger(__name__)


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
        logger.info(f"マネーフォワード勤怠: {self.url} にアクセス")
        self._page.goto(f"{self.url}/session/new")
        # TODO: マネーフォワード勤怠のログイン画面に合わせてセレクタを設定
        # self._page.fill('input[name="email"]', self.username)
        # self._page.click('button[type="submit"]')  # メールアドレス入力後に次へ
        # self._page.fill('input[name="password"]', self.password)
        # self._page.click('button[type="submit"]')
        # self._page.wait_for_url('**/attendance**')
        logger.info("マネーフォワード勤怠: ログイン (TODO: セレクタを設定してください)")

    def input_attendance(self, record: ShiftRecord):
        logger.info(
            f"マネーフォワード勤怠: 転記 {record.staff_name} {record.date} "
            f"{record.start_time.strftime('%H:%M')}〜{record.end_time.strftime('%H:%M')}"
        )
        # TODO: マネーフォワード勤怠の打刻編集画面に合わせて実装
        # 例:
        #   year, month, day = record.date.year, record.date.month, record.date.day
        #   self._page.goto(f"{self.url}/attendance/{year}/{month}")
        #   row = self._page.locator(f'tr[data-day="{day}"]')
        #   row.locator('.clock-in').fill(record.start_time.strftime('%H:%M'))
        #   row.locator('.clock-out').fill(record.end_time.strftime('%H:%M'))
        #   row.locator('button.save').click()
