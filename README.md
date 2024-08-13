## LinkedIn Activity Scraper

Skrip Python ini digunakan untuk mengekstrak data aktivitas terbaru dari profil LinkedIn yang diberikan. Skrip ini menggunakan library Playwright untuk melakukan otomatisasi browser dan mengekstrak data dari halaman aktivitas LinkedIn.

### Persyaratan
 - Python 3.6 atau lebih baru
 - Modul Python yang diperlukan (lihat requirements.txt)

### Instalasi
 
 1. Kloning repositori ini atau unduh file-file yang diperlukan.
 2. Buat file .env di direktori proyek dan tambahkan email dan password LinkedIn Anda:
 ```
 EMAIL_LINKED=your_email@example.com
 PASSWORD_LINKED=your_password
 ```
 3. Instal modul Python yang diperlukan dengan menjalankan perintah berikut:
 ```
 pip install -r requirements.txt
 ```

### Penggunaan

 1. Buka file url.txt dan tambahkan URL profil LinkedIn yang ingin Anda ekstrak aktivitasnya, satu URL per baris.
 2. Jalankan skrip dengan menjalankan perintah berikut:
 ```
 python main.py
 ```

Skrip akan membuka browser secara otomatis, masuk ke LinkedIn menggunakan kredensial yang diberikan, mengekstrak data aktivitas terbaru dari setiap URL yang diberikan, dan menyimpan data dalam format JSON di folder output.

### Catatan
 - Skrip ini menggunakan cookies untuk mempercepat proses login. Cookies akan disimpan di file data/cookies.json setelah login manual pertama kali.
 - Jika terjadi kesalahan atau timeout saat login, skrip akan mencoba muat ulang halaman dan melanjutkan proses.
 - Skrip ini mengasumsikan bahwa struktur HTML halaman LinkedIn tidak berubah secara signifikan. Jika terjadi perubahan, Anda mungkin perlu menyesuaikan kode untuk memilih elemen yang benar.