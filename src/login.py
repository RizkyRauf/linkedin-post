import os
import json
from datetime import datetime
from playwright.async_api import Page, TimeoutError

DATA_DIR = 'data'
COOKIES_FILE = os.path.join(DATA_DIR, 'cookies.json')

class LoginLinkedin:
    def __init__(self, page: Page, email: str, password: str):
        self.page = page
        self.email = email
        self.password = password
        os.makedirs(DATA_DIR, exist_ok=True)

    async def login(self):
        if await self.login_with_cookies():
            print("Berhasil login menggunakan cookies")
        else:
            await self.perform_manual_login()

    async def login_with_cookies(self):
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, 'r') as f:
                cookies = json.load(f)

            # Memeriksa tanggal kedaluwarsa setiap cookie
            valid_cookies = []
            for cookie in cookies:
                if 'expires' in cookie:
                    expires = cookie['expires']
                    if expires == -1 or expires > datetime.now().timestamp():
                        valid_cookies.append(cookie)

            # Menambahkan cookies yang valid ke browser
            if valid_cookies:
                await self.page.context.add_cookies(valid_cookies)
                return True

        return False

    async def perform_manual_login(self):
        await self.page.goto("https://www.linkedin.com/checkpoint/lg/sign-in-another-account")
        await self.page.fill('#username', self.email)
        await self.page.fill('#password', self.password)
        await self.page.click('button[aria-label="Sign in"]')

        try:
            await self.page.wait_for_load_state('networkidle', timeout=60000)
        except TimeoutError:
            print("Timeout terjadi saat menunggu halaman dimuat. Mencoba muat ulang halaman.")
            await self.page.reload()
            await self.page.wait_for_load_state('networkidle', timeout=60000)

        await self.save_cookies()
        print("Berhasil login secara manual")

    async def save_cookies(self):
        cookies = await self.page.context.cookies()
        with open(COOKIES_FILE, 'w') as f:
            json.dump(cookies, f)