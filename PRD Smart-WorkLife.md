## Product Requirements Document

## *Mobile App Smart-WorkLife*

| Document Owner | Nissa Zahra Zhafirah |
| :---- | :---- |
| Product Manager | Bintang Rafli Priatama |
| Designer | Nissa Zahra Zhafirah, Bintang Rafli Priatama |
| Tech Lead | Nissa Zahra Zhafirah, Bintang Rafli Priatama |
| Developer | Bintang Rafli Priatama, Nissa Zahra Zhafirah |
| QA | Nissa Zahra Zhafirah |

1. ### Latar Belakang dan Tujuan

#### 	1.1. Latar Belakang

* Tingginya tingkat burnout bagi pekerja kantoran, dimana data menurut web [worktime.com](http://worktime.com) bahwasanya pekerja kantoran hanya mampu bekerja fokus selama kurang lebih 2 jam 53 menit per shift 8 jam  
* Risiko kesehatan akibat gaya hidup sedentary (kurang gerak), dengan statistik menunjukkan lebih dari 50% pekerja kantoran mengalami nyeri punggung dan gangguan postur karena durasi duduk yang melebihi 6 jam per hari tanpa peregangan  
* Rendahnya tingkat hidrasi dan manajemen nutrisi personal, di mana pekerja cenderung mengabaikan asupan air meskipun dehidrasi ringan terbukti menurunkan fokus kognitif dan konsentrasi   
* Ketidakefektifan pemantauan kesehatan fisik mandiri, karena aplikasi kesehatan saat ini mayoritas hanya bersifat pengingat pasif tanpa adanya validasi gerakan (seperti deteksi pose nyata) untuk memastikan kualitas peregangan pengguna  
* Fragmentasi alat produktivitas, di mana pengguna harus berpindah antar 3-4 aplikasi berbeda untuk timer, kesehatan, to-do list, notes 

#### 	1.2. Tujuan

* Meningkatkan disiplin kerja menggunakan metode manajemen waktu (Pomodoro).  
* Menjaga kesehatan fisik pengguna melalui intervensi peregangan berbasis deteksi gerakan (MediaPipe).  
* Memastikan kebutuhan dasar biologis (minum dan makan) terpenuhi secara personal berdasarkan profil fisik pengguna (BMI).  
* Membangun ekosistem aplikasi asisten virtual yang terpadu bagi pekerja kantoran 

2. ### *Success Metrics*

* \[*Main*\] Jumlah pengguna yang menggunakan aplikasi setiap hari kerja   
* \[*Secondary*\] Persentase siklus Pomodoro yang diselesaikan sepenuhnya tanpa interupsi manual (stop/cancel)  
* \[*Secondary*\] Tingkat keberhasilan MediaPipe dalam mendeteksi 3 jenis gerakan utama  
* \[*Secondary*\] Pengguna mengikuti gerakan sesuai panduan visual di layar   
* \[*Secondary*\] Akurasi perhitungan BMI berdasarkan rumus standar WHO  
* \[*Secondary*\] Pengguna melakukan log "Minum" setelah menerima notifikasi algoritma.   
* \[*Secondary*\] Persentase tugas dalam To-Do List yang statusnya berubah menjadi "Done"  
* \[*Secondary*\] Tingkat kesalahan kata dalam Live Transcription (Speech-to-Text) di bawah 15% dalam kondisi ruangan tenang.   
* \[*Secondary*\] Penghematan waktu pembuatan notulen rapat dibandingkan cara manual 

3. ### *Requirements* (Kebutuhan) Aplikasi

#### 	3.1 Daftar *Requirement*

	

| Kode *Requirement* | *Requirement* |
| ----- | ----- |
| Halaman Home |  |
| REQ-001 | Pengguna dapat melihat ringkasan performa harian di dashboard yang mencakup metrik produktivitas, daftar tugas prioritas, serta status keseimbangan antara waktu kerja dan istirahat secara real-time |
| Halaman Smart Pomodoro |  |
| REQ-002 | Pengguna dapat menggunakan fitur manajemen waktu berbasis teknik Pomodoro dengan beberapa mode fokus (Klasik, Deep Work, Extend)  |
| Halaman Smart Stretching |  |
| REQ-003 | Pengguna dapat melakukan deteksi gerakan tubuh secara real-time menggunakan kamera |
| REQ-004 | Pengguna dapat melihat panduan visual gerakan peregangan yang harus dilakukan |
| REQ-005  | Pengguna dapat melihat jumlah repetisi gerakan serta mendapatkan peringatan jika posisi tidak sesuai. |
| Smart-Health |  |
| REQ-006 | Pengguna dapat menghitung nilai BMI untuk mengetahui kategori kondisi tubuh. |
| REQ-007 | Pengguna dapat memantau dan mengelola kebutuhan hidrasi harian.  |
| Smart-ToDoList |  |
| REQ-008 | Pengguna dapat mencatat daftar tugas pekerjaan dan mengatur tenggat waktu (deadline) untuk memantau prioritas kerja harian. |
| Smart-Notulen |  |
| REQ-009 | Pengguna dapat merekam audio rapat secara langsung untuk diubah menjadi teks. |
| REQ-010 | Pengguna dapat mengklik button “Generate Summary” untuk diringkas menjadi poin-poin penting oleh AI |

| REQ-011 | Pengguna dapat mendaftar akun baru menggunakan Email/Password atau melalui Google Login. |
| REQ-012 | Pengguna mendapatkan kode OTP via email setelah registrasi untuk verifikasi akun. |
| REQ-013 | Pengguna dapat masuk ke aplikasi menggunakan Email/Password atau Google Login. |
| REQ-014 | Pengguna dapat melakukan reset password jika lupa kata sandi. |

	3.2 Fitur di Luar Ruang Lingkup

* Semua komponen di header (profile dan notifikasi)  
* Preferensi Keadaan User (setelah user melakukan sign up)


	3.3 *Functional Requirements* (Kebutuhan Fungsional)

| *Requirement* | Spesifikasi |
| ----- | ----- |
| Autentikasi & Akun |  |
| Registrasi Akun | **Form Registrasi** Field Nama Lengkap, Email, Password, dan Konfirmasi Password. Validasi password minimal 8 karakter dan kecocokan konfirmasi password. **OTP Verification** Setelah submit, pengguna diarahkan ke halaman input kode OTP yang dikirim ke email. **Google Register** Integrasi OAuth2 Google untuk pendaftaran satu klik. |
| Login Akun | **Form Login** Field Email dan Password. **Forgot Password** Link "Lupa Password" untuk mengirim instruksi reset ke email. **Google Login** Integrasi OAuth2 Google untuk masuk tanpa input password. |
Server response
Code	Details
500
Undocumented
Error: Internal Server Error

Response body
Download
{
  "detail": "Internal server error: (sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.UndefinedColumnError'>: column users.is_verified does not exist\n[SQL: SELECT users.id, users.email, users.hashed_password, users.full_name, users.avatar_url, users.is_active, users.is_verified, users.otp_code, users.otp_expires_at, users.google_id, users.created_at, users.updated_at \nFROM users \nWHERE users.email = $1::VARCHAR]\n[parameters: ('admin@example.com',)]\n(Background on this error at: https://sqlalche.me/e/20/f405)"
}
Response headers
 content-length: 553 
 content-type: application/json 
 date: Wed,13 May 2026 09:15:15 GMT 
 server: uvicorn | Halaman Home |  |
| Pengguna dapat melihat ringkasan performa harian di dashboard yang mencakup metrik produktivitas, daftar tugas prioritas, serta status keseimbangan antara waktu kerja dan istirahat secara real-time. | **Productivity Overview Cards** Focus Time Card: Menampilkan akumulasi waktu fokus hari ini Break Time Card: Menampilkan total durasi istirahat  Tasks Done Card: Menampilkan persentase penyelesaian tugas, rasio jumlah tugas selesai terhadap total tugas  **Smart To-Do Section** Navigation Tabs: Pengguna dapat berpindah kategori tugas melalui tab "Penting", "Hari Ini", dan "Besok"  Task Item: Setiap tugas harus menampilkan *checkbox* untuk penyelesaian  Text Button “Lihat Semua” untuk membuka halaman Smart To-Do secara keseluruhan dan membuka halaman pembuatan tugas baru **Today’s Balance** Grafik lingkaran yang menampilkan skor efisiensi kerja dalam persentase Menampilkan detail durasi waktu kerja (*Work*) dan waktu istirahat (*Rest*) secara berdampingan |
| Halaman Smart-Pomodoro |  |
| Pengguna dapat menggunakan fitur manajemen waktu berbasis teknik Pomodoro dengan beberapa mode fokus (Klasik, Deep Work, Extend)  | **Mode Timer**  Tersedia tiga pilihan mode yaitu Klasik (25 menit fokus dan 5 menit istirahat), Deep Work (50 menit fokus dan 10 menit istirahat), serta Extend yang memungkinkan pengaturan durasi fokus dan istirahat secara fleksibel. **Timer Control** Tersedia kontrol berupa tombol Start, Pause, dan Reset. Timer berjalan secara real-time serta dapat dihentikan atau diulang sesuai kebutuhan. **Session Tracking**Jumlah sesi fokus yang telah diselesaikan dapat ditampilkan, termasuk total akumulasi waktu fokus dalam satu hari. **Notifikasi**Notifikasi otomatis diberikan ketika sesi fokus selesai dan saat waktu istirahat dimulai untuk membantu perpindahan aktivitas. **Visual Feedback**  Ditampilkan indikator visual seperti countdown timer atau progress bar yang menunjukkan status sesi, baik saat fokus maupun istirahat. |
| Halaman Smart-Stretching |  |
| Pengguna dapat melakukan deteksi gerakan tubuh secara real-time menggunakan kamera. | Menggunakan kamera depan untuk menangkap pergerakan tubuh selama sesi peregangan Mendeteksi koordinat tubuh secara real-time menggunakan MediaPipe Pose Menampilkan hasil deteksi untuk memantau posisi tubuh secara langsung |
| Pengguna dapat melihat panduan visual gerakan peregangan yang harus dilakukan. | Menampilkan panduan gerakan peregangan berupa gambar atau animasi Menampilkan nama gerakan pada setiap sesi Menampilkan durasi pelaksanaan untuk setiap gerakan  |
| Pengguna dapat melihat jumlah repetisi gerakan serta mendapatkan peringatan jika posisi tidak sesuai. | Menghitung jumlah repetisi gerakan secara otomatis selama sesi berlangsung Menampilkan jumlah repetisi secara real-time di layar Memberikan peringatan apabila posisi tubuh tidak sesuai dengan gerakan yang benar Memberikan umpan balik untuk membantu pengguna memperbaiki posisi gerakan |
| Halaman Smart-Health |  |
| Pengguna dapat menghitung nilai BMI untuk mengetahui kategori kondisi tubuh. | Menerima input tinggi dan berat badan untuk perhitungan BMI Menghitung nilai BMI secara otomatis berdasarkan input pengguna Menampilkan kategori BMI (Underweight, Normal, Overweight, Obese) Terdapat button “edit” untuk perubahan kondisi berat dan tinggi badan pengguna |
| Pengguna dapat memantau dan mengelola kebutuhan hidrasi harian.  | Menghitung kebutuhan konsumsi air harian berdasarkan berat badan Terdapat button notifikasi pengingat air minum. Menyediakan pengaturan interval pengingat sesuai kebutuhan Menampilkan jumlah konsumsi air dan progres terhadap target harian dalam bentuk visual  |
| Halaman Smart-ToDoList |  |
| Pengguna dapat mencatat daftar tugas pekerjaan dan mengatur tenggat waktu (*deadline*) untuk memantau prioritas kerja harian.  | Tersedia button “+” untuk menambahkan tugas Field teks untuk judul tugas, pemilihan tanggal dan jam deadline, tersedia juga button toggle untuk menandai kategori prioritas  Tugas otomatis dikelompokkan sesuai kategori “Penting”, “Hari Ini”, “Besok” Checkbox untuk menandai tugas selesai yang akan memindahkan tugas ke bagian "Selesai"  |
| Halaman Smart-Notulen |  |
| Pengguna dapat merekam audio rapat secara langsung untuk diubah menjadi teks  | Menampilkan visualisasi gelombang suara (*waveform*) saat proses perekaman berlangsung Menampilkan teks yang muncul secara *real-time* saat tombol rekam ditekan menggunakan Speech-to-Text API.  Sistem akan memberikan peringatan jika rekaman sudah mencapai durasi maksimal (misal 60 menit) untuk menjaga performa memori perangkat.  |
| Pengguna dapat mengklik button “Generate Summary” untuk diringkas menjadi poin-poin penting oleh AI | Button "Generate Summary" yang mengirim transkrip ke model AI untuk menghasilkan poin-poin penting dan *Action Items*.  Button “Simpan Notulen” untuk menyimpan hasil ringkasan ke Arsip notulen dengan menampilkan pop up Judul Notulen dan Tanggal dibuatnya Notulen  |

# 