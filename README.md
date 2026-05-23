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
├── donanim_gui_vFinal.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── ses_ikon/
    ├── dark.svg
    ├── light.svg
    ├── search.svg
    ├── copy.svg
    ├── volume_up.svg
    ├── volume_off.svg
    └── b_agiz_sesi.wav
````

## Kurulum

Python 3.10 veya üzeri önerilir.

Gerekli paketleri kurmak için:

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python donanim_gui_vFinal.py
```

## Windows EXE Oluşturma

```bash
pyinstaller --onefile --windowed ^
--add-data "ses_ikon;ses_ikon" ^
donanim_gui_vFinal.py
```

## Linux Build

```bash
pyinstaller --onefile \
--windowed \
--add-data "ses_ikon:ses_ikon" \
donanim_gui_vFinal.py
```

## macOS Build

```bash
pyinstaller --onefile \
--windowed \
--add-data "ses_ikon:ses_ikon" \
donanim_gui_vFinal.py
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
ses_ikon/b_agiz_sesi.wav
```

## İkon Sistemi

SVG ikonları `ses_ikon` klasöründe tutulur.
Uygulama gerekli durumlarda SVG dosyalarını otomatik PNG’ye dönüştürür.

## Notlar

* Windows üzerinde en kapsamlı donanım bilgisi alınır.
* Linux ve macOS desteği vardır; ancak bazı donanım detayları sistem izinlerine ve kullanılan komutlara göre sınırlı olabilir.
* PSU marka/model/watt bilgisi çoğu sistemde yazılımsal olarak okunamaz.
* LibreHardwareMonitor desteği yalnızca Windows tarafında anlamlıdır.

## Lisans

MIT License

```
```
