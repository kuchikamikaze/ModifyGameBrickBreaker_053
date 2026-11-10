![alt text](image.png)

# Modify Game Brick Breaker

## Perubahan dari Versi Awal

- **Kontrol platform:** Tombol panah kiri dan kanan menggerakkan platform terus-menerus selama ditekan, dengan respons lebih cepat.
- **Ukuran dan gerak platform:** Platform dibuat lebih tipis. Bola hanya memantul dari sisi atas platform, dengan arah pantulan mengikuti posisi benturan.
- **Kecepatan bola:** Kecepatan bola dinaikkan sedikit dari 10 menjadi 11.
- **Layer balok:** Setiap 8 balok hancur, balok yang tersisa turun satu baris dan satu layer baru muncul di bagian atas. Susunan warna layer awal tidak diacak; pada layer baru, setiap balok memiliki peluang 30% menjadi biru.
- **Batas permainan:** Permainan berakhir jika balok turun sampai menyentuh batas atas platform.
- **Skor:** Setiap balok yang hancur memberi 100 poin. Skor ditampilkan di pojok kanan atas.
- **Power-up jatuh:** Balok yang hancur memiliki peluang 20% menjatuhkan power-up. Platform dapat menangkap dan mengaktifkannya.
- **Power-up bola tiga:** Menambahkan dua bola sehingga bola yang mendapat efek ini menjadi tiga.
- **Power-up bola tambahan:** Meluncurkan satu bola tambahan dari atas platform.
- **Power-up tembus:** Bola dapat menembus balok merah dengan kapasitas tiga. Balok biru menghabiskan dua kapasitas dan memantulkan bola.
- **Power-up hapus baris:** Menghancurkan seluruh balok pada baris terbawah, termasuk jika baris itu hanya memiliki satu balok.
- **Komentar kode:** Komentar berbahasa Indonesia ditambahkan untuk menjelaskan bagian-bagian utama program.

