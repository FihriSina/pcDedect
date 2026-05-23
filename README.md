# Donanım Bilgi Uygulaması

Modern arayüze sahip, çoklu işletim sistemi destekli gelişmiş donanım analiz uygulaması.

Python + CustomTkinter ile geliştirilmiştir.

---

# Özellikler

- Modern ve akıcı arayüz
- Windows / Linux / macOS desteği
- Sistem bilgisi görüntüleme
- Laptop algılama sistemi
- İşlemci bilgisi
- Anakart bilgisi
- Ekran kartı + VRAM bilgisi
- RAM bilgisi
- SSD / HDD ayrımı
- Bluetooth cihaz analizi
- Çevre birimi tespiti
- PSU / güç sensörü desteği
- Batarya durumu görüntüleme
- Karanlık / aydınlık tema desteği
- SVG ikon sistemi
- Ses efektli kart animasyonları
- Google arama entegrasyonu
- Sahibinden + Letgo pazar araması
- Kopyalama sistemi
- Özel uygulama ikonu
- Portable ZIP oluşturma desteği
- Platform bağımsız mimari

---

# Desteklenen İşletim Sistemleri

| İşletim Sistemi | Destek |
|---|---|
| Windows | Tam Destek |
| Linux | Büyük Ölçüde Destek |
| macOS | Büyük Ölçüde Destek |

---

# Proje Yapısı

```text
PCDETECT/
│
├── app/
│   └── donanim_gui_vFinal.py
│
├── assets/
│   ├── app.ico
│   ├── app_logo.png
│   │
│   ├── ikonlar/
│   │   ├── dark.svg
│   │   ├── light.svg
│   │   ├── search.svg
│   │   ├── copy.svg
│   │   ├── market.svg
│   │   ├── volume_up.svg
│   │   └── volume_off.svg
│   │
│   └── sesler/
│       └── b_agiz_sesi.wav
│
├── build.bat
├── make_portable.bat
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Kurulum

Python 3.10 veya üzeri önerilir.

Gerekli paketleri kur:

```bash
pip install -r requirements.txt
```

---

# Çalıştırma

Proje ana klasöründeyken:

```bash
python app/donanim_gui_vFinal.py
```

---

# Windows EXE Oluşturma

Windows üzerinde tek dosyalık `.exe` oluşturmak için:

```bash
build.bat
```

Çıktı:

```text
dist/donanim_gui_vFinal.exe
```

---

# Portable ZIP Oluşturma

Önce:

```bash
build.bat
```

çalıştırılmalıdır.

Sonrasında:

```bash
make_portable.bat
```

Çıktı:

```text
release/DonanimBilgi_Portable.zip
```

---

# Manuel PyInstaller Build

Windows:

```bash
python -m PyInstaller ^
--onefile ^
--windowed ^
--icon "assets\app.ico" ^
--hidden-import customtkinter ^
--hidden-import PIL ^
--hidden-import cairosvg ^
--collect-submodules customtkinter ^
--collect-submodules PIL ^
--collect-submodules cairosvg ^
--add-data "assets;assets" ^
app\donanim_gui_vFinal.py
```

Linux/macOS:

```bash
python -m PyInstaller \
--onefile \
--windowed \
--add-data "assets:assets" \
app/donanim_gui_vFinal.py
```

---

# Arama Sistemi

- **Ara** butonu Google araması açar.
- **Pazar** butonu aynı anda:
  - Sahibinden
  - Letgo

sekmesini açar.

Arama metinleri otomatik sadeleştirilir.

Örnek:

```text
Micro-Star International Co., Ltd.
```

otomatik olarak:

```text
MSI
```

şeklinde optimize edilir.

---

# Laptop Algılama Sistemi

Uygulama cihazın laptop olup olmadığını otomatik algılar.

Laptop cihazlarda:

```text
Laptop
```

kartı görünür.

Masaüstü sistemlerde bu kart gizlenir.

Kart içerisinde:

- Marka
- Model
- Versiyon

bilgileri gösterilir.

Seri numarası gibi kişisel bilgiler özellikle filtrelenir.

---

# Ses Sistemi

Kart açılışlarında özel ses sistemi kullanılır.

Özellikler:

- Fade-in / fade-out
- Ses patlaması azaltma
- Dinamik ses parçalama
- Thread-safe oynatma
- Çoklu kart sesi senkronizasyonu

Ses dosyası:

```text
assets/sesler/b_agiz_sesi.wav
```

---

# İkon Sistemi

SVG ikonları:

```text
assets/ikonlar/
```

klasöründe tutulur.

Uygulama gerekli durumlarda SVG dosyalarını otomatik PNG’ye dönüştürür.

---

# Build Sistemi

## build.bat

Windows `.exe` build alır.

## make_portable.bat

EXE dosyasını portable ZIP’e dönüştürür.

---

# Teknik Mimari

Uygulama:

- modüler
- asset tabanlı
- cross-platform
- taşınabilir
- PyInstaller uyumlu

bir yapı üzerine geliştirilmiştir.

Kod mimarisi ileride:

- gerçek zamanlı sensörler
- benchmark sistemi
- overlay sistemi
- AI destekli analiz
- sürücü kontrol sistemi

gibi özelliklerin eklenmesine uygundur.

---

# Gelecek Planlanan Özellikler

- CPU/GPU sıcaklık sensörleri
- Gerçek zamanlı RAM/CPU grafikleri
- FPS monitörü
- Benchmark sistemi
- Driver kontrol sistemi
- Ağ cihazları analizi
- Çoklu dil desteği
- Splash screen
- Otomatik güncelleme sistemi

---

# AI / GPT Development Note

Bu proje AI destekli geliştirilmektedir.

README dosyası:
- proje mimarisini,
- klasör yapısını,
- build sistemini,
- asset sistemini,
- uygulama mantığını

koruyacak şekilde hazırlanmıştır.

Projeyi devam ettirecek başka bir AI/GPT:
- mevcut klasör yapısını bozmamalı,
- asset yollarını değiştirmemeli,
- build sistemini kırmamalı,
- cross-platform yapıyı korumalı,
- README yapısını mümkün olduğunca sürdürmelidir.

---

# Notlar

- Windows üzerinde en kapsamlı donanım bilgisi alınır.
- Linux/macOS tarafında bazı bilgiler sistem izinlerine göre sınırlı olabilir.
- PSU marka/model/watt bilgisi çoğu sistemde yazılımsal olarak okunamaz.
- LibreHardwareMonitor desteği yalnızca Windows tarafında anlamlıdır.

---

# Lisans

MIT License