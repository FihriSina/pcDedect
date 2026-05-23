# Donanım Bilgi Uygulaması

Modern arayüze sahip, çoklu işletim sistemi destekli gelişmiş donanım analiz uygulaması.  
Python + CustomTkinter ile geliştirilmiştir.

## Özellikler

- Modern ve akıcı arayüz
- Windows / Linux / macOS desteği
- Sistem bilgisi görüntüleme
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
- Kopyalama butonu
- Özel uygulama ikonu
- Portable ZIP oluşturma desteği
- Platform bağımsız mimari

## Desteklenen İşletim Sistemleri

| İşletim Sistemi | Destek |
|---|---|
| Windows | Tam Destek |
| Linux | Büyük Ölçüde Destek |
| macOS | Büyük Ölçüde Destek |

## Proje Yapısı

```text
proje/
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
````

## Kurulum

Python 3.10 veya üzeri önerilir.

Gerekli paketleri kurmak için:

```bash
pip install -r requirements.txt
```

## Çalıştırma

Proje ana klasöründeyken:

```bash
python app/donanim_gui_vFinal.py
```

## Windows EXE Oluşturma

Windows üzerinde tek dosyalık `.exe` oluşturmak için:

```bash
build.bat
```

Bu işlemden sonra çıktı şu klasörde oluşur:

```text
dist/donanim_gui_vFinal.exe
```

## Portable ZIP Oluşturma

Önce `build.bat` çalıştırılmalıdır.

Daha sonra portable ZIP oluşturmak için:

```bash
make_portable.bat
```

Çıktı şu klasörde oluşur:

```text
release/DonanimBilgi_Portable.zip
```

## Manuel PyInstaller Komutu

Windows için manuel build almak istersen:

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

## Linux Build

Linux için:

```bash
python -m PyInstaller \
--onefile \
--windowed \
--add-data "assets:assets" \
app/donanim_gui_vFinal.py
```

## macOS Build

macOS için:

```bash
python -m PyInstaller \
--onefile \
--windowed \
--add-data "assets:assets" \
app/donanim_gui_vFinal.py
```

## Arama Sistemi

* **Ara** butonu Google araması açar.
* **Pazar** butonu aynı anda Sahibinden ve Letgo araması açar.

Arama metinleri otomatik temizlenir ve sadeleştirilir.

Örnek:

```text
Micro-Star International Co., Ltd.
```

şuna dönüştürülür:

```text
MSI
```

## Ses Sistemi

Kart açılışlarında özel ses sistemi kullanılır.

* Fade-in / fade-out desteği
* Ses patlamasını azaltma
* Dinamik ses parçalama
* Thread-safe ses oynatma

Ses dosyası:

```text
assets/sesler/b_agiz_sesi.wav
```

## İkon Sistemi

SVG ikonları şu klasörde tutulur:

```text
assets/ikonlar/
```

Uygulama gerekli durumlarda SVG dosyalarını otomatik PNG’ye dönüştürür.

## Build Dosyaları

### build.bat

Windows için `.exe` üretir.

### make_portable.bat

Oluşturulan `.exe` dosyasını portable ZIP formatına çevirir.

## Notlar

* Windows üzerinde en kapsamlı donanım bilgisi alınır.
* Linux ve macOS desteği vardır; ancak bazı donanım detayları sistem izinlerine ve kullanılan komutlara göre sınırlı olabilir.
* PSU marka/model/watt bilgisi çoğu sistemde yazılımsal olarak okunamaz.
* LibreHardwareMonitor desteği yalnızca Windows tarafında anlamlıdır.
* `build/`, `dist/`, `release/` ve `*.spec` dosyaları GitHub’a yüklenmemelidir.

## Lisans

MIT License

```
```
