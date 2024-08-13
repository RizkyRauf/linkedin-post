import os
import re
import json
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
from src.login import LoginLinkedin  # Assuming LoginLinkedin is defined elsewhere
from playwright.async_api import async_playwright, TimeoutError


# Memuat file .env
load_dotenv()

# Mengambil email dan password dari file .env
email = os.getenv('EMAIL_LINKED')
password = os.getenv('PASSWORD_LINKED')

def parse_date(date_str):
    """Mengubah string tanggal menjadi objek datetime."""
    try:
        # Menghapus karakter " •" dan semua karakter setelahnya
        cleaned_date_str = re.sub(r' •.*', '', date_str)

        # Mengganti singkatan dengan kata lengkap
        cleaned_date_str = cleaned_date_str.replace('d', ' day').replace('mo', ' month').replace('w', ' week').replace('yr', ' year')

        # Mengurai tanggal menggunakan modul datetime
        parts = cleaned_date_str.split()
        if parts[-1] == 'day':
            days_ago = int(parts[0])
            return datetime.now() - timedelta(days=days_ago)
        elif parts[-1] == 'month':
            months_ago = int(parts[0])
            return datetime.now() - timedelta(days=months_ago * 30)  # Asumsi 1 bulan = 30 hari
        elif parts[-1] == 'week':
            weeks_ago = int(parts[0])
            return datetime.now() - timedelta(days=weeks_ago * 7)
        elif parts[-1] == 'year':
            years_ago = int(parts[0])
            return datetime.now() - timedelta(days=years_ago * 365)  # Asumsi 1 tahun = 365 hari
        else:
            return datetime.strptime(cleaned_date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Error parsing date: {date_str}")
        return None  # atau beberapa nilai tanggal default

async def scroll_to_bottom(page):
    last_height = await page.evaluate("document.body.scrollHeight")
    while True:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(2)
        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

async def extract_data(page):
    data = []
    try:
        # Extract data after scrolling
        element_cards = await page.query_selector_all('//li[@class="profile-creator-shared-feed-update__container"]')
        for card in element_cards:
            # Mengambil elemen nama
            name_element = await card.query_selector('//*[@id="fie-impression-container"]/div[1]/div[1]/div/div/a/span[1]/span[1]/span/span[2]')
            name = await name_element.inner_text() if name_element else None

            # Mengambil elemen tanggal
            date_element = await card.query_selector('.update-components-actor__sub-description span')  # More relative path
            date_str = await date_element.inner_text() if date_element else None
            date = parse_date(date_str) if date_str else None
            print(date)

            # Mengambil elemen teks
            text_element = await card.query_selector('.update-components-text')  # Assuming this class is more stable
            text = await text_element.inner_text() if text_element else None

            # Menambahkan data ke dalam daftar jika semua elemen ditemukan
            if name and date and text:
                data.append({
                    "name": name,
                    "date": date.strftime('%Y-%m-%d') if date else None,
                    "text": text
                })

    except TimeoutError:
        print("Element not found within the given time.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return data

async def click_load_more_button(page):
    retries = 3
    while retries > 0:
        try:
            load_more_button = await page.query_selector('button.scaffold-finite-scroll__load-button')
            if load_more_button:
                await load_more_button.click()
                await asyncio.sleep(2)  # Give time for the new content to load
                return True
            else:
                return False
        except Exception as e:
            print(f"Error saat mengklik tombol 'Tampilkan hasil lainnya': {e}")
            retries -= 1
            await asyncio.sleep(2)  # Wait before retrying
    return False

async def main(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        login = LoginLinkedin(page, email, password)
        await login.login()

        await page.wait_for_load_state('networkidle')

        try:
            await page.goto(f"{url}recent-activity/all/")
            print(f"mengakses halaman: {url}")
            await asyncio.sleep(2)

            # Scroll ke bawah dan klik tombol "Tampilkan hasil lainnya"
            while True:
                await scroll_to_bottom(page)
                if not await click_load_more_button(page):
                    break  # Exit loop if no button is found or all retries failed

            data = await extract_data(page)

            # Menyimpan data ke dalam file JSON
            profile_name = url.split('/')[-2]  # Mengambil nama profil dari URL
            output_folder = 'output'
            os.makedirs(output_folder, exist_ok=True)  # Membuat folder jika belum ada
            output_file = os.path.join(output_folder, f"{profile_name}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Data telah disimpan ke {output_file}")

        except Exception as e:
            print(f"Error saat mengakses halaman: {e}")

        await browser.close()

if __name__ == "__main__":
    url = "http://www.linkedin.com/in/farahdh11/"
    # with open('url.txt', 'r') as f:
    #     url = f.readline().strip()
    #     for line in f:
    #         url = line.strip()
    #         asyncio.run(main(url))
