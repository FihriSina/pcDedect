import customtkinter as ctk
import subprocess
import json
import threading
from datetime import datetime
import webbrowser
from urllib.parse import quote_plus
import wave
import math
import struct
import tempfile
import os
import sys
import platform
import shutil

CURRENT_OS = platform.system()
IS_WINDOWS = CURRENT_OS == "Windows"
IS_MACOS = CURRENT_OS == "Darwin"
IS_LINUX = CURRENT_OS == "Linux"

try:
    import wmi
except:
    wmi = None

try:
    import pythoncom
except:
    pythoncom = None

try:
    import winreg
except:
    winreg = None

try:
    import winsound
except:
    winsound = None

try:
    from PIL import Image
except:
    Image = None

try:
    import cairosvg
except:
    cairosvg = None

ASSET_FOLDER = "assets"

CUSTOM_SOUND_FILE = os.path.join(
    ASSET_FOLDER,
    "sesler",
    "b_agiz_sesi.wav"
)

ICON_FILES = {
    "dark": "dark.svg",
    "light": "light.svg",
    "search": "search.svg",
    "volume_off": "volume_off.svg",
    "volume_up": "volume_up.svg",
    "copy": "copy.svg",
}


def get_windows_theme_mode():
    if not IS_WINDOWS or winreg is None:
        return "light"

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return "light" if int(value) == 1 else "dark"
    except:
        return "light"


def get_wmi_connection(namespace=None):
    if not IS_WINDOWS or wmi is None:
        return None

    try:
        if namespace:
            return wmi.WMI(namespace=namespace)
        return wmi.WMI()
    except:
        return None


def run_command(command):
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        return completed.stdout.strip()
    except:
        return ""


def command_exists(command):
    return shutil.which(command) is not None


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


INVALID_VALUES = {
    "",
    "none",
    "null",
    "unknown",
    "bilinmiyor",
    "to be filled by o.e.m.",
    "to be filled by oem",
    "system serial number",
    "default string",
    "not specified",
    "not available",
    "n/a",
    "0",
    "00000000",
    "0000000000",
    "ffffffff",
}

GENERIC_DEVICE_NAMES = {
    "hid-compliant mouse",
    "hid-compliant consumer control device",
    "hid-compliant vendor-defined device",
    "hid-compliant system controller",
    "hid keyboard device",
    "enhanced (101- or 102-key)",
    "standard ps/2 keyboard",
    "standard ps/2 mouse",
    "usb input device",
    "usb composite device",
    "usb root hub",
    "generic usb hub",
    "generic bluetooth adapter",
    "bluetooth device",
    "bluetooth radio",
    "bluetooth peripheral device",
    "bluetooth hid device",
    "device identification service",
    "object push service",
    "sim access service",
    "headset audio gateway service",
    "phonebook access pse service",
    "personal area network service",
    "personal area network nap service",
    "nearbysharing",
    "sms/mms",
    "btis",
    "gearmanager",
    "samsungdevice",
    "uuid128",
    "deviceid",
    "generic pnp monitor",
    "pnp monitor",
    "audio endpoint",
    "high definition audio device",
    "usb audio device",
    "nvidia high definition audio",
    "remote desktop device redirector bus",
    "microsoft bluetooth enumerator",
    "microsoft bluetooth le enumerator",
    "microsoft kernel debug network adapter",
    "microsoft basic display adapter",
}

GENERIC_NAME_CONTAINS = [
    "hid-compliant",
    "usb input device",
    "usb composite device",
    "usb root hub",
    "generic usb hub",
    "generic pnp monitor",
    "microsoft bluetooth enumerator",
    "bluetooth le enumerator",
    "bluetooth peripheral device",
    "bluetooth device (",
    "standard ps/2",
    "enhanced (101- or 102-key)",
    "audio endpoint",
    "high definition audio device",
    "nvidia high definition audio",
    "nvidia virtual audio",
    "hands-free hf",
    "hands-free ag",
    "avrcp transport",
    "a2dp snk",
    "serial over bluetooth",
    "device identification service",
    "object push service",
    "sim access service",
    "headset audio gateway service",
    "phonebook access",
    "personal area network",
    "nearbysharing",
    "sms/mms",
    "sppservice",
    "remote desktop",
    "wan miniport",
]


def bytes_to_gb(value):
    try:
        return round(int(value) / (1024 ** 3))
    except:
        return None


def clean_text(value):
    if value is None:
        return "Bilinmiyor"
    return str(value).strip()


def is_valid_value(value):
    if value is None:
        return False

    text = str(value).strip()
    normalized = text.lower()

    if normalized in INVALID_VALUES:
        return False

    if len(text) < 2:
        return False

    return True


def is_useful_device_name(value):
    if not is_valid_value(value):
        return False

    text = clean_text(value)
    normalized = text.lower()

    if normalized in GENERIC_DEVICE_NAMES:
        return False

    for bad_text in GENERIC_NAME_CONTAINS:
        if bad_text in normalized:
            return False

    return True


def add_if_valid(parts, value):
    if is_valid_value(value):
        text = clean_text(value)
        joined = " ".join(parts).lower()

        if text.lower() not in joined:
            parts.append(text)


def dedupe_items(items):
    seen = set()
    result = []

    for item in items:
        key = item.strip().lower()
        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def normalize_search_text(text):
    text = clean_text(text)

    prefixes = [
        "Monitör:", "Klavye:", "Mouse:", "Kamera:", "Kamera / Görüntüleme:",
        "Ses / Medya:", "Ses Aygıtı:", "USB Aygıtı:", "Bluetooth:", "BIOS:"
    ]

    for prefix in prefixes:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()

    removable_phrases = [
        "VRAM bilgisi okunamadı",
        "Tür: Unspecified",
        "Tür: Bilinmiyor",
        "Tür: Unknown",
    ]

    for phrase in removable_phrases:
        text = text.replace(phrase, "").strip()

    return " ".join(text.split())


def normalize_marketplace_search_text(text):
    text = normalize_search_text(text)

    replacements = {
        "Micro-Star International Co., Ltd.": "MSI",
        "Micro-Star International": "MSI",
        "MICRO-STAR INTERNATIONAL": "MSI",
        "Co., Ltd.": "",
        "CO., LTD.": "",
        "Corporation": "",
        "Inc.": "",
        "Ltd.": "",
        "Socket": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    removable_words = [
        "VRAM",
        "GB VRAM",
        "Bilinmiyor",
        "bilgisi okunamadı",
    ]

    for word in removable_words:
        text = text.replace(word, "")

    return " ".join(text.split())


def is_searchable_item(text):
    raw_text = clean_text(text)
    normalized_raw = raw_text.lower()
    text = normalize_search_text(raw_text)
    lowered = text.lower()

    if not is_useful_device_name(text):
        return False

    blocked_phrases = [
        "bilgi bulunamadı",
        "okunamadı",
        "tespit edilemedi",
        "bulunamadı",
        "psu marka",
        "güç kaynağı etiketi",
        "batarya durumu",
        "şarj yüzdesi",
        "son güncelleme",
    ]

    if any(phrase in lowered for phrase in blocked_phrases):
        return False

    if normalized_raw.startswith("bios:"):
        return False

    searchable_keywords = [
        "intel", "amd", "ryzen", "core", "nvidia", "geforce", "radeon",
        "asus", "msi", "micro-star", "gigabyte", "asrock", "lenovo",
        "dell", "hp", "acer", "samsung", "kingston", "crucial", "corsair",
        "g.skill", "western digital", "wd", "seagate", "toshiba", "sandisk",
        "logitech", "razer", "steelseries", "hyperx", "jbl", "sony",
        "viewsonic", "aoc", "lg", "philips", "benq", "cloud", "buds",
    ]

    if any(keyword in lowered for keyword in searchable_keywords):
        return True

    has_letter = any(char.isalpha() for char in text)
    has_digit = any(char.isdigit() for char in text)
    has_model_separator = any(separator in text for separator in ["-", "_", "/"])

    if has_letter and has_digit and len(text) >= 6:
        return True

    if has_letter and has_digit and has_model_separator:
        return True

    return False


def memory_type_name(code):
    types = {
        20: "DDR",
        21: "DDR2",
        24: "DDR3",
        26: "DDR4",
        34: "DDR5"
    }
    return types.get(code, "RAM")


def battery_status_name(code):
    statuses = {
        1: "Deşarj oluyor",
        2: "Şarj oluyor / AC güce bağlı",
        3: "Tam dolu",
        4: "Düşük",
        5: "Kritik",
        6: "Şarj oluyor",
        7: "Şarj oluyor ve yüksek",
        8: "Şarj oluyor ve düşük",
        9: "Şarj oluyor ve kritik",
        10: "Bilinmiyor",
        11: "Kısmen şarj oldu"
    }

    try:
        return statuses.get(int(code), f"Bilinmeyen durum kodu: {code}")
    except:
        return "Bilinmiyor"


def get_gpu_vram_from_registry():
    results = {}

    if not IS_WINDOWS or winreg is None:
        return results

    try:
        base_path = r"SYSTEM\CurrentControlSet\Control\Video"

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path) as video_key:
            for i in range(winreg.QueryInfoKey(video_key)[0]):
                guid = winreg.EnumKey(video_key, i)

                for sub in ["0000", "0001"]:
                    try:
                        path = base_path + "\\" + guid + "\\" + sub

                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as adapter_key:
                            name, _ = winreg.QueryValueEx(adapter_key, "DriverDesc")
                            memory, _ = winreg.QueryValueEx(
                                adapter_key,
                                "HardwareInformation.qwMemorySize"
                            )

                            gb = bytes_to_gb(memory)

                            if name and gb:
                                results[name.lower()] = gb

                    except:
                        pass

    except:
        pass

    return results


def get_system_info():
    items = []
    c = get_wmi_connection()

    if c is None:
        node = platform.node()
        if node:
            items.append(f"Bilgisayar adı: {node}")
        items.append(f"İşletim sistemi: {platform.platform()}")
        machine = platform.machine()
        if machine:
            items.append(f"Mimari: {machine}")
        return dedupe_items(items)

    try:
        for system in c.Win32_ComputerSystemProduct():
            parts = []
            add_if_valid(parts, getattr(system, "Vendor", None))
            add_if_valid(parts, getattr(system, "Name", None))
            add_if_valid(parts, getattr(system, "Version", None))

            if parts:
                items.append(" ".join(parts))

    except:
        pass

    try:
        for bios in c.Win32_BIOS():
            parts = ["BIOS:"]
            add_if_valid(parts, getattr(bios, "Name", None))
            add_if_valid(parts, getattr(bios, "SMBIOSBIOSVersion", None))

            if len(parts) > 1:
                items.append(" ".join(parts))

    except:
        pass

    if not items:
        items.append("Bilgi bulunamadı.")

    return dedupe_items(items)


def get_cpu_info():
    items = []
    c = get_wmi_connection()

    if c is None:
        cpu_name = platform.processor()

        if not cpu_name and IS_LINUX:
            cpu_name = run_command(["bash", "-lc", "grep -m1 'model name' /proc/cpuinfo | cut -d ':' -f2-"]).strip()

        if not cpu_name and IS_MACOS:
            cpu_name = run_command(["sysctl", "-n", "machdep.cpu.brand_string"])

        items.append(cpu_name if cpu_name else "İşlemci bilgisi sınırlı olarak okunamadı.")
        return dedupe_items(items)

    try:
        for cpu in c.Win32_Processor():
            parts = []
            add_if_valid(parts, getattr(cpu, "Name", None))
            add_if_valid(parts, getattr(cpu, "SocketDesignation", None))

            if parts:
                items.append(" ".join(parts))
    except:
        pass

    return dedupe_items(items)


def get_motherboard_info():
    items = []
    c = get_wmi_connection()

    if c is None:
        if IS_LINUX:
            vendor = run_command(["bash", "-lc", "cat /sys/class/dmi/id/board_vendor 2>/dev/null"])
            name = run_command(["bash", "-lc", "cat /sys/class/dmi/id/board_name 2>/dev/null"])
            version = run_command(["bash", "-lc", "cat /sys/class/dmi/id/board_version 2>/dev/null"])
            parts = []
            add_if_valid(parts, vendor)
            add_if_valid(parts, name)
            add_if_valid(parts, version)
            if parts:
                items.append(" ".join(parts))

        elif IS_MACOS:
            model = run_command(["sysctl", "-n", "hw.model"])
            if model:
                items.append(f"Apple {model}")

        if not items:
            items.append("Anakart bilgisi bu işletim sisteminde sınırlı olarak okunamadı.")

        return dedupe_items(items)

    try:
        for board in c.Win32_BaseBoard():
            parts = []
            add_if_valid(parts, getattr(board, "Manufacturer", None))
            add_if_valid(parts, getattr(board, "Product", None))
            add_if_valid(parts, getattr(board, "Version", None))

            if parts:
                items.append(" ".join(parts))
    except:
        pass

    return dedupe_items(items)


def get_gpu_info():
    items = []
    c = get_wmi_connection()
    registry_vram = get_gpu_vram_from_registry()

    if c is None:
        if IS_MACOS:
            output = run_command(["system_profiler", "SPDisplaysDataType"])
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("Chipset Model:"):
                    items.append(line.replace("Chipset Model:", "").strip())

        elif IS_LINUX and command_exists("lspci"):
            output = run_command(["bash", "-lc", "lspci | grep -Ei 'vga|3d|display'"])
            for line in output.splitlines():
                if line.strip():
                    items.append(line.strip())

        if not items:
            items.append("Ekran kartı bilgisi bu işletim sisteminde sınırlı olarak okunamadı.")

        return dedupe_items(items)

    try:
        for gpu in c.Win32_VideoController():
            name = clean_text(getattr(gpu, "Name", None))
            vram_gb = bytes_to_gb(getattr(gpu, "AdapterRAM", None))

            for reg_name, reg_vram in registry_vram.items():
                if name.lower() in reg_name or reg_name in name.lower():
                    vram_gb = reg_vram
                    break

            if vram_gb:
                line = f"{name} {vram_gb} GB VRAM"
            else:
                line = f"{name} VRAM bilgisi okunamadı"

            items.append(line)
    except:
        pass

    return dedupe_items(items)


def get_ram_info():
    items = []
    c = get_wmi_connection()

    if c is None:
        if IS_MACOS:
            memory = run_command(["sysctl", "-n", "hw.memsize"])
            size = bytes_to_gb(memory)
            if size:
                items.append(f"Toplam RAM {size} GB")

        elif IS_LINUX:
            output = run_command(["bash", "-lc", "grep MemTotal /proc/meminfo | awk '{print $2}'"])
            try:
                size = round(int(output) / (1024 ** 2))
                items.append(f"Toplam RAM {size} GB")
            except:
                pass

        if not items:
            items.append("RAM modül marka/model bilgisi bu işletim sisteminde sınırlı olarak okunamadı.")

        return dedupe_items(items)

    try:
        for ram in c.Win32_PhysicalMemory():
            parts = []
            add_if_valid(parts, getattr(ram, "Manufacturer", None))
            add_if_valid(parts, getattr(ram, "PartNumber", None))

            ram_type = memory_type_name(getattr(ram, "SMBIOSMemoryType", None))
            if ram_type != "RAM":
                parts.append(ram_type)

            speed = getattr(ram, "ConfiguredClockSpeed", None)
            if not speed:
                speed = getattr(ram, "Speed", None)

            if speed:
                parts.append(f"{speed} MHz")

            size = bytes_to_gb(getattr(ram, "Capacity", None))
            if size:
                parts.append(f"{size} GB")

            if parts:
                items.append(" ".join(parts))
    except:
        pass

    return dedupe_items(items)


def run_powershell_json(command):
    if not IS_WINDOWS:
        return []

    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        output = completed.stdout.strip()

        if not output:
            return []

        data = json.loads(output)

        if isinstance(data, dict):
            return [data]

        return data

    except:
        return []


def get_storage_info():
    ssd_items = []
    hdd_items = []
    unknown_items = []

    if not IS_WINDOWS:
        if IS_MACOS:
            output = run_command(["diskutil", "list"])
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("/dev/disk"):
                    unknown_items.append(line)

        elif IS_LINUX and command_exists("lsblk"):
            output = run_command(["lsblk", "-d", "-o", "NAME,MODEL,SIZE,ROTA,TYPE"])
            for line in output.splitlines()[1:]:
                parts = line.split()
                if len(parts) < 3:
                    continue

                disk_type = parts[-1]
                rota = parts[-2]
                readable = " ".join(parts[:-2]).strip()

                if disk_type != "disk":
                    continue

                if rota == "0":
                    ssd_items.append(readable)
                elif rota == "1":
                    hdd_items.append(readable)
                else:
                    unknown_items.append(readable)

        if not ssd_items and not hdd_items and not unknown_items:
            unknown_items.append("Depolama bilgisi bu işletim sisteminde sınırlı olarak okunamadı.")

        return dedupe_items(ssd_items), dedupe_items(hdd_items), dedupe_items(unknown_items)

    command = """
    Get-PhysicalDisk |
    Select-Object FriendlyName, MediaType, Size |
    ConvertTo-Json
    """

    disks = run_powershell_json(command)

    if disks:
        for disk in disks:
            name = clean_text(disk.get("FriendlyName"))
            media_type = clean_text(disk.get("MediaType"))
            size = bytes_to_gb(disk.get("Size"))

            line = f"{name}"

            if size:
                line += f" {size} GB"

            if media_type.lower() == "ssd":
                ssd_items.append(line)
            elif media_type.lower() == "hdd":
                hdd_items.append(line)
            else:
                unknown_items.append(f"{line} Tür: {media_type}")

    else:
        c = get_wmi_connection()

        if c is not None:
            try:
                for disk in c.Win32_DiskDrive():
                    name = clean_text(getattr(disk, "Model", None))
                    size = bytes_to_gb(getattr(disk, "Size", None))
                    media_type = clean_text(getattr(disk, "MediaType", None))

                    line = f"{name}"

                    if size:
                        line += f" {size} GB"

                    unknown_items.append(f"{line} Tür: {media_type}")
            except:
                pass

    return dedupe_items(ssd_items), dedupe_items(hdd_items), dedupe_items(unknown_items)


def get_battery_info():
    items = []
    c = get_wmi_connection()

    if c is None:
        if IS_LINUX and command_exists("upower"):
            output = run_command(["bash", "-lc", "upower -e | grep -m1 battery | xargs -r upower -i"])
            for line in output.splitlines():
                clean_line = line.strip()
                if clean_line.startswith("model:"):
                    items.append("Batarya adı: " + clean_line.replace("model:", "").strip())
                elif clean_line.startswith("state:"):
                    items.append("Batarya durumu: " + clean_line.replace("state:", "").strip())
                elif clean_line.startswith("percentage:"):
                    items.append("Şarj yüzdesi: " + clean_line.replace("percentage:", "").strip())

        elif IS_MACOS:
            output = run_command(["pmset", "-g", "batt"])
            if output:
                items.append(output.replace("\n", " "))

        if not items:
            items.append("Batarya bilgisi bulunamadı veya bu işletim sisteminde sınırlı.")

        return dedupe_items(items)

    try:
        for battery in c.Win32_Battery():
            name = clean_text(getattr(battery, "Name", None))
            percent = clean_text(getattr(battery, "EstimatedChargeRemaining", None))
            status_code = getattr(battery, "BatteryStatus", None)
            status = battery_status_name(status_code)

            items.append(f"Batarya adı: {name}")
            items.append(f"Batarya durumu: {status}")
            items.append(f"Şarj yüzdesi: %{percent}")
    except:
        pass

    if not items:
        items.append("Batarya bilgisi bulunamadı. Masaüstü bilgisayarlarda normaldir.")

    return dedupe_items(items)


def get_lhm_power_sensor_info():
    items = []

    if not IS_WINDOWS:
        items.append("PSU marka, model ve watt bilgisi yazılımsal olarak okunamadı.")
        items.append("Bu bilgi için güç kaynağı etiketi kontrol edilmelidir.")
        return items

    try:
        lhm = get_wmi_connection(namespace=r"root\LibreHardwareMonitor")
        if lhm is None:
            raise Exception("LibreHardwareMonitor WMI namespace bulunamadı")

        sensors = lhm.Sensor()
        wanted_types = ["Voltage", "Current", "Power"]

        for sensor in sensors:
            sensor_type = clean_text(getattr(sensor, "SensorType", None))
            name = clean_text(getattr(sensor, "Name", None))
            value = getattr(sensor, "Value", None)

            if sensor_type in wanted_types and value is not None:
                try:
                    numeric_value = round(float(value), 2)
                except:
                    numeric_value = value

                if sensor_type == "Voltage":
                    unit = "V"
                elif sensor_type == "Current":
                    unit = "A"
                elif sensor_type == "Power":
                    unit = "W"
                else:
                    unit = ""

                items.append(f"{name}: {numeric_value} {unit}")

    except:
        pass

    if not items:
        items.append("PSU marka, model ve watt bilgisi yazılımsal olarak okunamadı.")
        items.append("Bu bilgi için güç kaynağı etiketi kontrol edilmelidir.")

    return dedupe_items(items)


def get_monitor_info():
    items = []
    c = get_wmi_connection()

    if c is None:
        if IS_MACOS:
            output = run_command(["system_profiler", "SPDisplaysDataType"])
            for line in output.splitlines():
                clean_line = line.strip()
                if "Resolution:" in clean_line:
                    items.append(clean_line)

        elif IS_LINUX and command_exists("xrandr"):
            output = run_command(["bash", "-lc", "xrandr --query | grep ' connected'"])
            for line in output.splitlines():
                items.append(line.strip())

        return dedupe_items(items)

    try:
        for monitor in c.Win32_DesktopMonitor():
            parts = []
            add_if_valid(parts, getattr(monitor, "Name", None))
            add_if_valid(parts, getattr(monitor, "MonitorManufacturer", None))
            add_if_valid(parts, getattr(monitor, "MonitorType", None))

            width = getattr(monitor, "ScreenWidth", None)
            height = getattr(monitor, "ScreenHeight", None)

            if width and height:
                parts.append(f"{width}x{height}")

            if parts:
                line = " ".join(parts)
                if is_useful_device_name(line):
                    items.append(line)

    except:
        pass

    try:
        for device in c.Win32_PnPEntity():
            pnp_class = clean_text(getattr(device, "PNPClass", None)).lower()
            name = clean_text(getattr(device, "Name", None))

            if pnp_class == "monitor" and is_useful_device_name(name):
                items.append(name)

    except:
        pass

    return dedupe_items(items)


def get_peripheral_info():
    wired_items = []
    bluetooth_items = []
    c = get_wmi_connection()

    if c is None:
        monitor_items = get_monitor_info()
        for item in monitor_items:
            wired_items.append(f"Monitör: {item}")

        if IS_MACOS:
            usb_output = run_command(["system_profiler", "SPUSBDataType"])
            bt_output = run_command(["system_profiler", "SPBluetoothDataType"])

            for line in usb_output.splitlines():
                clean_line = line.strip().rstrip(":")
                if is_useful_device_name(clean_line) and len(clean_line) > 3:
                    wired_items.append(f"USB Aygıtı: {clean_line}")

            for line in bt_output.splitlines():
                clean_line = line.strip().rstrip(":")
                if is_useful_device_name(clean_line) and len(clean_line) > 3:
                    bluetooth_items.append(clean_line)

        elif IS_LINUX:
            if command_exists("lsusb"):
                output = run_command(["lsusb"])
                for line in output.splitlines():
                    if is_useful_device_name(line):
                        wired_items.append(f"USB Aygıtı: {line}")

            if command_exists("bluetoothctl"):
                output = run_command(["bash", "-lc", "bluetoothctl devices 2>/dev/null"])
                for line in output.splitlines():
                    if is_useful_device_name(line):
                        bluetooth_items.append(line)

        if not wired_items:
            wired_items.append("Kablolu veya dahili çevre birimi bilgisi bulunamadı.")

        if not bluetooth_items:
            bluetooth_items.append("Bluetooth aygıt bilgisi bulunamadı.")

        return dedupe_items(wired_items), dedupe_items(bluetooth_items)

    monitor_items = get_monitor_info()
    for item in monitor_items:
        wired_items.append(f"Monitör: {item}")

    bluetooth_keywords = [
        "buds", "airpods", "galaxy buds", "jbl", "sony", "anker",
        "logitech", "razer", "steelseries", "hyperx", "corsair",
        "wireless controller", "xbox", "dualsense", "controller",
        "mouse", "keyboard", "headset", "speaker", "sina"
    ]

    wired_keywords = [
        "logitech", "razer", "steelseries", "hyperx", "corsair",
        "asus", "lenovo", "hp", "dell", "acer", "msi", "gigabyte",
        "webcam", "camera", "keyboard", "mouse", "receiver",
        "headset", "speaker", "microphone", "monitor", "controller"
    ]

    useful_classes = {
        "keyboard": "Klavye",
        "mouse": "Mouse",
        "pointingdevice": "Mouse",
        "camera": "Kamera",
        "image": "Kamera / Görüntüleme",
        "media": "Ses / Medya",
        "audioendpoint": "Ses Aygıtı",
        "usb": "USB Aygıtı",
        "bluetooth": "Bluetooth",
    }

    try:
        for device in c.Win32_PnPEntity():
            name = clean_text(getattr(device, "Name", None))
            pnp_class = clean_text(getattr(device, "PNPClass", None)).lower()
            device_id = clean_text(getattr(device, "DeviceID", None)).lower()
            manufacturer = clean_text(getattr(device, "Manufacturer", None))
            lowered_name = name.lower()

            if not is_useful_device_name(name):
                continue

            is_bluetooth = (
                pnp_class == "bluetooth"
                or "bthenum" in device_id
                or "bluetooth" in lowered_name
                or "bluetooth" in manufacturer.lower()
            )

            if is_bluetooth:
                if any(keyword in lowered_name for keyword in bluetooth_keywords):
                    clean_name = name
                    for removable in [
                        " Hands-Free HF", " Hands-Free AG", " Avrcp Transport",
                        " A2DP SNK", " Audio Gateway Service"
                    ]:
                        clean_name = clean_name.replace(removable, "")
                    bluetooth_items.append(clean_name)
                continue

            if pnp_class in useful_classes:
                if pnp_class in {"media", "audioendpoint"}:
                    if "nvidia" in lowered_name or "high definition audio" in lowered_name:
                        continue
                    if "hands-free" in lowered_name or "buds" in lowered_name:
                        continue

                if not any(keyword in lowered_name for keyword in wired_keywords):
                    continue

                label = useful_classes[pnp_class]
                wired_items.append(f"{label}: {name}")

    except:
        pass

    try:
        for keyboard in c.Win32_Keyboard():
            name = clean_text(getattr(keyboard, "Name", None))
            if is_useful_device_name(name) and any(k in name.lower() for k in wired_keywords):
                wired_items.append(f"Klavye: {name}")
    except:
        pass

    try:
        for mouse in c.Win32_PointingDevice():
            name = clean_text(getattr(mouse, "Name", None))
            if is_useful_device_name(name) and any(k in name.lower() for k in wired_keywords):
                wired_items.append(f"Mouse: {name}")
    except:
        pass

    try:
        for sound in c.Win32_SoundDevice():
            name = clean_text(getattr(sound, "Name", None))
            lowered_name = name.lower()
            if not is_useful_device_name(name):
                continue
            if "nvidia" in lowered_name or "high definition audio" in lowered_name:
                continue
            if "hands-free" in lowered_name or "buds" in lowered_name:
                continue
            if any(keyword in lowered_name for keyword in wired_keywords):
                wired_items.append(f"Ses Aygıtı: {name}")
    except:
        pass

    wired_items = dedupe_items(wired_items)
    bluetooth_items = dedupe_items(bluetooth_items)

    if not wired_items:
        wired_items.append("Kablolu veya dahili çevre birimi bilgisi bulunamadı.")

    if not bluetooth_items:
        bluetooth_items.append("Bluetooth aygıt bilgisi bulunamadı.")

    return wired_items, bluetooth_items


class HardwareApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Donanım Bilgi Uygulaması")
        self.geometry("1000x720")
        self.minsize(850, 600)
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.sidebar_separator = ctk.CTkFrame(
            self,
            width=2,
            corner_radius=0,
            fg_color="#1F6AA5"
        )
        self.sidebar_separator.grid(row=0, column=1, sticky="ns")

        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.grid(row=0, column=2, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="Sistem Bilgisi",
            font=("Segoe UI", 24, "bold")
        )
        self.title_label.pack(pady=(30, 10), padx=20)

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Donanım envanteri",
            font=("Segoe UI", 13),
            text_color="gray"
        )
        self.subtitle_label.pack(pady=(0, 30), padx=20)

        self.refresh_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.refresh_frame.pack(pady=10, padx=20, fill="x")
        self.refresh_frame.grid_columnconfigure(0, weight=1)

        self.refresh_button = ctk.CTkButton(
            self.refresh_frame,
            text="Bilgileri Yenile",
            command=self.refresh_data
        )
        self.refresh_button.grid(row=0, column=0, sticky="ew")

        self.spinner_label = ctk.CTkLabel(
            self.refresh_frame,
            text="",
            width=26,
            height=26,
            font=("Segoe UI", 18, "bold"),
            text_color="#3B8ED0"
        )
        self.spinner_label.grid(row=0, column=1, padx=(8, 0))
        self.spinner_label.grid_remove()

        self.sound_enabled = True
        self.animation_enabled = True
        self.current_theme = get_windows_theme_mode()
        self.icons = {}
        self.load_icons()
        self.spinner_running = False
        self.spinner_index = 0
        self.spinner_angle = 0
        self.spinner_symbols = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.custom_sound_parts = []
        self.card_sound_index = 0
        self.sound_lock = threading.Lock()
        self.blup_sound_path = self.create_blup_sound_file()
        self.load_custom_sound_parts()

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="Hazır",
            font=("Segoe UI", 12),
            text_color="gray",
            wraplength=170
        )
        self.status_label.pack(pady=(5, 10), padx=20)

        self.note = ctk.CTkLabel(
            self.sidebar,
            text="Metin alanlarındaki bilgileri seçip Ctrl+C ile kopyalayabilirsin.",
            font=("Segoe UI", 12),
            text_color="gray",
            wraplength=170,
            justify="left"
        )
        self.note.pack(pady=30, padx=20)

        self.top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 5))
        self.top_bar.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkLabel(
            self.top_bar,
            text="Bilgisayar Donanım Bilgileri",
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        )
        self.header.grid(row=0, column=0, sticky="w")

        self.sound_icon_button = ctk.CTkButton(
            self.top_bar,
            text="" if self.icons.get("volume_up") else "🔊",
            image=self.icons.get("volume_up"),
            width=38,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 17),
            command=self.toggle_sound
        )
        self.sound_icon_button.grid(row=0, column=1, padx=(8, 4))

        current_theme_icon = self.icons.get("light") if self.current_theme == "light" else self.icons.get("dark")
        current_theme_text = "☀" if self.current_theme == "light" else "☾"

        self.theme_icon_button = ctk.CTkButton(
            self.top_bar,
            text="" if current_theme_icon else current_theme_text,
            image=current_theme_icon,
            width=38,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 17),
            command=self.toggle_theme
        )
        self.theme_icon_button.grid(row=0, column=2, padx=(4, 0))

        self.content = ctk.CTkScrollableFrame(self.main)
        self.content.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        self.content.grid_columnconfigure(0, weight=1)

        self.refresh_data()

    def set_theme(self, mode):
        ctk.set_appearance_mode(mode)

    def get_app_folder(self):
        try:
            return os.path.dirname(os.path.abspath(__file__))
        except:
            return os.getcwd()

    def get_resource_base_folder(self):
        try:
            return sys._MEIPASS
        except:
            return self.get_app_folder()

    def get_asset_path(self, file_name):
        return os.path.join(self.get_resource_base_folder(), ASSET_FOLDER, file_name)

    def svg_to_png_if_needed(self, svg_path):
        if not os.path.exists(svg_path):
            return None

        png_path = os.path.splitext(svg_path)[0] + "_icon.png"

        if os.path.exists(png_path):
            return png_path

        if cairosvg is None:
            return None

        try:
            cairosvg.svg2png(
                url=svg_path,
                write_to=png_path,
                output_width=64,
                output_height=64
            )
            return png_path
        except:
            return None

    def load_single_icon(self, file_name, size=(19, 19)):
        if Image is None:
            return None

        svg_path = self.get_asset_path(file_name)
        png_path = self.svg_to_png_if_needed(svg_path)

        if png_path is None or not os.path.exists(png_path):
            return None

        try:
            image = Image.open(png_path)
            return ctk.CTkImage(light_image=image, dark_image=image, size=size)
        except:
            return None

    def load_icons(self):
        self.icons = {
            name: self.load_single_icon(file_name)
            for name, file_name in ICON_FILES.items()
        }

    def toggle_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
            ctk.set_appearance_mode("dark")
            icon = self.icons.get("dark")
            self.theme_icon_button.configure(
                text="" if icon else "☾",
                image=icon
            )
        else:
            self.current_theme = "light"
            ctk.set_appearance_mode("light")
            icon = self.icons.get("light")
            self.theme_icon_button.configure(
                text="" if icon else "☀",
                image=icon
            )

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled

        if self.sound_enabled:
            icon = self.icons.get("volume_up")
            self.sound_icon_button.configure(
                text="" if icon else "🔊",
                image=icon
            )
        else:
            icon = self.icons.get("volume_off")
            self.sound_icon_button.configure(
                text="" if icon else "🔇",
                image=icon
            )

    def create_blup_sound_file(self):
        try:
            sample_rate = 44100
            duration = 0.18
            total_samples = int(sample_rate * duration)
            path = os.path.join(tempfile.gettempdir(), "pcdetect_blup.wav")

            with wave.open(path, "w") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)

                for i in range(total_samples):
                    t = i / sample_rate
                    progress = i / total_samples
                    envelope = math.sin(math.pi * progress) ** 0.75
                    base_frequency = 260 + (540 * progress)
                    wobble = math.sin(2 * math.pi * 18 * t) * 35
                    frequency = base_frequency + wobble
                    sample = math.sin(2 * math.pi * frequency * t)
                    bubble = 0.35 * math.sin(2 * math.pi * (frequency * 1.85) * t)
                    value = int((sample + bubble) * envelope * 11500)
                    wav_file.writeframes(struct.pack("<h", value))

            return path
        except:
            return None

    def get_custom_sound_path(self):
        return self.get_asset_path(CUSTOM_SOUND_FILE)

    def get_frame_amplitude(self, frame_bytes, sample_width):
        if not frame_bytes:
            return 0

        if sample_width == 1:
            values = [abs(byte - 128) for byte in frame_bytes]
            return sum(values) / max(1, len(values))

        if sample_width == 2:
            count = len(frame_bytes) // 2
            if count <= 0:
                return 0
            values = struct.unpack("<" + "h" * count, frame_bytes[:count * 2])
            return sum(abs(value) for value in values) / count

        return 0

    def apply_sound_fade(self, raw_data, sample_width, channels, frame_rate, fade_ms=35):
        if not raw_data or sample_width != 2:
            return raw_data

        bytes_per_frame = channels * sample_width
        total_frames = len(raw_data) // bytes_per_frame
        fade_frames = int(frame_rate * fade_ms / 1000)
        fade_frames = min(fade_frames, max(1, total_frames // 3))

        if total_frames <= 2 or fade_frames <= 0:
            return raw_data

        samples_count = len(raw_data) // 2
        samples = list(struct.unpack("<" + "h" * samples_count, raw_data[:samples_count * 2]))

        for frame_index in range(total_frames):
            if frame_index < fade_frames:
                factor = frame_index / fade_frames
            elif frame_index >= total_frames - fade_frames:
                factor = (total_frames - frame_index - 1) / fade_frames
            else:
                factor = 1.0

            if factor < 1.0:
                for channel in range(channels):
                    sample_index = frame_index * channels + channel
                    if 0 <= sample_index < len(samples):
                        samples[sample_index] = int(samples[sample_index] * factor)

        return struct.pack("<" + "h" * len(samples), *samples)

    def load_custom_sound_parts(self):
        self.custom_sound_parts = []
        source_path = self.get_custom_sound_path()

        if not os.path.exists(source_path):
            return

        try:
            with wave.open(source_path, "rb") as source:
                channels = source.getnchannels()
                sample_width = source.getsampwidth()
                frame_rate = source.getframerate()
                total_frames = source.getnframes()
                raw_data = source.readframes(total_frames)

            chunk_ms = 10
            frames_per_chunk = max(1, int(frame_rate * chunk_ms / 1000))
            bytes_per_frame = channels * sample_width
            bytes_per_chunk = frames_per_chunk * bytes_per_frame

            chunks = []
            amplitudes = []

            for start in range(0, len(raw_data), bytes_per_chunk):
                chunk = raw_data[start:start + bytes_per_chunk]
                amplitude = self.get_frame_amplitude(chunk, sample_width)
                chunks.append((start, start + len(chunk), amplitude))
                amplitudes.append(amplitude)

            if not amplitudes:
                return

            max_amplitude = max(amplitudes)
            if max_amplitude <= 0:
                return

            threshold = max_amplitude * 0.06
            min_active_chunks = 2
            min_silence_chunks = 7
            padding_chunks = 8

            ranges = []
            active_start = None
            silence_count = 0
            active_count = 0

            for index, (_, _, amplitude) in enumerate(chunks):
                is_active = amplitude >= threshold

                if is_active:
                    if active_start is None:
                        active_start = index
                        active_count = 0
                    active_count += 1
                    silence_count = 0
                else:
                    if active_start is not None:
                        silence_count += 1
                        if silence_count >= min_silence_chunks:
                            active_end = index - silence_count
                            if active_count >= min_active_chunks:
                                ranges.append((active_start, active_end))
                            active_start = None
                            silence_count = 0
                            active_count = 0

            if active_start is not None and active_count >= min_active_chunks:
                ranges.append((active_start, len(chunks) - 1))

            temp_folder = os.path.join(tempfile.gettempdir(), "pcdetect_sound_parts")
            os.makedirs(temp_folder, exist_ok=True)

            for part_index, (start_chunk, end_chunk) in enumerate(ranges, start=1):
                start_chunk = max(0, start_chunk - padding_chunks)
                end_chunk = min(len(chunks) - 1, end_chunk + padding_chunks)

                start_byte = chunks[start_chunk][0]
                end_byte = chunks[end_chunk][1]
                part_data = raw_data[start_byte:end_byte]
                part_data = self.apply_sound_fade(
                    part_data,
                    sample_width,
                    channels,
                    frame_rate,
                    fade_ms=35
                )

                if not part_data:
                    continue

                part_path = os.path.join(temp_folder, f"blop_part_{part_index:02d}.wav")
                with wave.open(part_path, "wb") as part_file:
                    part_file.setnchannels(channels)
                    part_file.setsampwidth(sample_width)
                    part_file.setframerate(frame_rate)
                    part_file.writeframes(part_data)

                self.custom_sound_parts.append(part_path)

        except:
            self.custom_sound_parts = []

    def play_pop_sound(self):
        if not self.sound_enabled or winsound is None:
            return

        try:
            if self.custom_sound_parts:
                sound_path = self.custom_sound_parts[self.card_sound_index % len(self.custom_sound_parts)]
                self.card_sound_index += 1
            elif self.blup_sound_path and os.path.exists(self.blup_sound_path):
                sound_path = self.blup_sound_path
            else:
                sound_path = None

            def sound_job(path):
                try:
                    with self.sound_lock:
                        if path:
                            winsound.PlaySound(path, winsound.SND_FILENAME)
                        else:
                            winsound.MessageBeep(winsound.MB_OK)
                except:
                    pass

            threading.Thread(target=sound_job, args=(sound_path,), daemon=True).start()

        except:
            pass

    def start_refresh_spinner(self):
        self.spinner_running = True
        self.spinner_index = 0
        self.spinner_angle = 0
        self.spinner_label.grid()
        self.update_refresh_spinner()

    def update_refresh_spinner(self):
        if not self.spinner_running:
            return

        symbol = self.spinner_symbols[self.spinner_index % len(self.spinner_symbols)]
        self.spinner_label.configure(text=symbol)
        self.spinner_index += 1
        self.after(50, self.update_refresh_spinner)

    def stop_refresh_spinner(self):
        self.spinner_running = False
        self.spinner_label.grid_remove()
        self.spinner_label.configure(text="")
        self.refresh_button.configure(text="Bilgileri Yenile")

    def refresh_data(self):
        self.card_sound_index = 0
        self.refresh_button.configure(
            text="Yenileniyor",
            state="disabled"
        )
        self.start_refresh_spinner()

        self.status_label.configure(
            text="Bölümler sırayla yükleniyor..."
        )

        self.clear_content()

        try:
            self.content._parent_canvas.yview_moveto(0)
        except:
            pass

        self.loading_label = ctk.CTkLabel(
            self.content,
            text="Donanım bilgileri hazırlanıyor...",
            font=("Segoe UI", 18, "bold")
        )
        self.loading_label.pack(pady=80)

        thread = threading.Thread(
            target=self.load_data_background,
            daemon=True
        )
        thread.start()

    def remove_loading_label(self):
        try:
            if hasattr(self, "loading_label") and self.loading_label.winfo_exists():
                self.loading_label.destroy()
        except:
            pass

    def add_card_progressively(self, title, items, searchable=True, delay=0):
        self.after(
            delay,
            lambda title=title, items=items, searchable=searchable: self._add_card_after_loading(title, items, searchable)
        )

    def _add_card_after_loading(self, title, items, searchable=True):
        self.remove_loading_label()
        card = self.add_card(title, items, searchable=searchable)

        if self.animation_enabled:
            self.animate_card_entry(card)

        self.play_pop_sound()

    def animate_card_entry(self, card, step=0):
        if not self.animation_enabled:
            return

        colors = ["#2B6EA6", "#2E5F8F", "transparent"]

        if step >= len(colors):
            return

        try:
            card.configure(border_width=1 if step < 2 else 0, border_color=colors[step])
            self.after(75, lambda: self.animate_card_entry(card, step + 1))
        except:
            pass

    def finish_refresh(self):
        now = datetime.now().strftime("%H:%M:%S")

        self.status_label.configure(
            text=f"Son güncelleme: {now}"
        )

        self.stop_refresh_spinner()
        self.refresh_button.configure(
            state="normal"
        )

    def load_data_background(self):
        if pythoncom is not None:
            pythoncom.CoInitialize()

        try:
            delay = 0
            first_pause = 2000
            step_delay = 500
            alerts = []

            self.after(0, lambda: self.status_label.configure(text="Bilgisayar / BIOS yükleniyor..."))
            system_items = get_system_info()
            self.add_card_progressively("Bilgisayar / BIOS", system_items, delay=delay)
            delay += first_pause

            self.after(0, lambda: self.status_label.configure(text="İşlemci bilgisi yükleniyor..."))
            cpu_items = get_cpu_info()
            self.add_card_progressively("İşlemci", cpu_items, delay=delay)
            delay += step_delay

            self.after(0, lambda: self.status_label.configure(text="Anakart bilgisi yükleniyor..."))
            motherboard_items = get_motherboard_info()
            self.add_card_progressively("Anakart", motherboard_items, delay=delay)
            delay += step_delay

            self.after(0, lambda: self.status_label.configure(text="Ekran kartı bilgisi yükleniyor..."))
            gpu_items = get_gpu_info()
            if any("VRAM bilgisi okunamadı" in item for item in gpu_items):
                alerts.append("Uyarı: Bazı ekran kartlarında VRAM bilgisi Windows tarafından okunamadı.")
            self.add_card_progressively("Ekran Kartı", gpu_items, delay=delay)
            delay += step_delay

            self.after(0, lambda: self.status_label.configure(text="RAM bilgisi yükleniyor..."))
            ram_items = get_ram_info()
            self.add_card_progressively("RAM", ram_items, delay=delay)
            delay += step_delay

            self.after(0, lambda: self.status_label.configure(text="Depolama bilgisi yükleniyor..."))
            ssd_items, hdd_items, unknown_storage = get_storage_info()
            self.add_card_progressively("Depolama / SSD", ssd_items, delay=delay)
            delay += step_delay
            self.add_card_progressively("Depolama / HDD", hdd_items, delay=delay)
            delay += step_delay

            if unknown_storage:
                alerts.append("Uyarı: Bazı depolama birimlerinde SSD/HDD türü belirlenemedi.")
                self.add_card_progressively("Depolama / Türü Belirsiz", unknown_storage, delay=delay)
                delay += step_delay

            self.after(0, lambda: self.status_label.configure(text="Çevre birimleri yükleniyor..."))
            wired_items, bluetooth_items = get_peripheral_info()
            self.add_card_progressively("Çevre Birimleri / Kablolu ve Dahili", wired_items, delay=delay)
            delay += step_delay
            self.add_card_progressively("Çevre Birimleri / Bluetooth", bluetooth_items, delay=delay)
            delay += step_delay

            self.after(0, lambda: self.status_label.configure(text="Güç bilgisi yükleniyor..."))
            battery_items = get_battery_info()

            if battery_items and "Batarya bilgisi bulunamadı" not in battery_items[0]:
                self.add_card_progressively("Güç / Batarya", battery_items, delay=delay)
                delay += step_delay
            else:
                power_sensor_items = get_lhm_power_sensor_info()
                if any("PSU marka, model ve watt bilgisi" in item for item in power_sensor_items):
                    alerts.append("Uyarı: PSU veya güç sensörü bilgisi okunamadı. LibreHardwareMonitor kapalı olabilir ya da anakart sensör desteği sunmuyor olabilir.")
                self.add_card_progressively("Güç / PSU ve Sensörler", power_sensor_items, delay=delay)
                delay += step_delay

            alerts = dedupe_items(alerts)
            if alerts:
                self.add_card_progressively("Eksik Bilgi Uyarıları", alerts, searchable=False, delay=delay)
                delay += step_delay

            self.after(delay + 50, self.finish_refresh)

        except Exception as error:
            error_message = str(error)
            self.after(0, lambda error_message=error_message: self.show_error(error_message))
        finally:
            if pythoncom is not None:
                pythoncom.CoUninitialize()

    def collect_all_data(self):
        ssd_items, hdd_items, unknown_storage = get_storage_info()
        wired_items, bluetooth_items = get_peripheral_info()
        gpu_items = get_gpu_info()
        power_sensor_items = get_lhm_power_sensor_info()

        alerts = []

        if any("VRAM bilgisi okunamadı" in item for item in gpu_items):
            alerts.append("Uyarı: Bazı ekran kartlarında VRAM bilgisi Windows tarafından okunamadı.")

        if unknown_storage:
            alerts.append("Uyarı: Bazı depolama birimlerinde SSD/HDD türü belirlenemedi.")

        if any("PSU marka, model ve watt bilgisi" in item for item in power_sensor_items):
            alerts.append("Uyarı: PSU veya güç sensörü bilgisi okunamadı. LibreHardwareMonitor kapalı olabilir ya da anakart sensör desteği sunmuyor olabilir.")

        return {
            "system": get_system_info(),
            "cpu": get_cpu_info(),
            "motherboard": get_motherboard_info(),
            "gpu": gpu_items,
            "ram": get_ram_info(),
            "ssd": ssd_items,
            "hdd": hdd_items,
            "unknown_storage": unknown_storage,
            "battery": get_battery_info(),
            "power_sensors": power_sensor_items,
            "wired_peripherals": wired_items,
            "bluetooth_peripherals": bluetooth_items,
            "alerts": dedupe_items(alerts),
        }

    def update_ui_with_data(self, data):
        self.clear_content()

        self.add_card("Bilgisayar / BIOS", data["system"])
        self.add_card("İşlemci", data["cpu"])
        self.add_card("Anakart", data["motherboard"])
        self.add_card("Ekran Kartı", data["gpu"])
        self.add_card("RAM", data["ram"])
        self.add_card("Depolama / SSD", data["ssd"])
        self.add_card("Depolama / HDD", data["hdd"])

        if data["unknown_storage"]:
            self.add_card("Depolama / Türü Belirsiz", data["unknown_storage"])

        if data["alerts"]:
            self.add_card("Eksik Bilgi Uyarıları", data["alerts"], searchable=False)

        self.add_card("Çevre Birimleri / Kablolu ve Dahili", data["wired_peripherals"])
        self.add_card("Çevre Birimleri / Bluetooth", data["bluetooth_peripherals"])

        if data["battery"] and "Batarya bilgisi bulunamadı" not in data["battery"][0]:
            self.add_card("Güç / Batarya", data["battery"])
        else:
            self.add_card("Güç / PSU ve Sensörler", data["power_sensors"])

        now = datetime.now().strftime("%H:%M:%S")

        self.status_label.configure(
            text=f"Son güncelleme: {now}"
        )

        self.stop_refresh_spinner()
        self.refresh_button.configure(
            state="normal"
        )

    def show_error(self, message):
        self.clear_content()

        self.add_card(
            "Hata",
            [
                "Bilgiler okunurken hata oluştu.",
                message
            ]
        )

        self.status_label.configure(text="Hata oluştu")

        self.stop_refresh_spinner()
        self.refresh_button.configure(
            text="Bilgileri Yenile",
            state="normal"
        )

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def search_on_google(self, query):
        query = normalize_search_text(query)

        if not query:
            return

        url = "https://www.google.com/search?q=" + quote_plus(query)
        webbrowser.open(url)

    def search_on_marketplaces(self, query):
        query = normalize_marketplace_search_text(query)

        if not query:
            return

        encoded_query = quote_plus(query)

        sahibinden_url = "https://www.sahibinden.com/arama?query_text=" + encoded_query
        letgo_url = "https://www.letgo.com/arama?isSearchCall=true&query_text=" + encoded_query

        webbrowser.open_new_tab(sahibinden_url)
        webbrowser.open_new_tab(letgo_url)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_label.configure(text="Kopyalandı")

    def add_card(self, title, items, searchable=True):
        card = ctk.CTkFrame(self.content, corner_radius=18)

        card.pack(fill="x", padx=5, pady=10)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=18, pady=(15, 5))

        if not items:
            items = ["Bilgi bulunamadı."]

        for item in items:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=4)
            row.grid_columnconfigure(0, weight=1)

            textbox = ctk.CTkTextbox(
                row,
                height=34,
                font=("Consolas", 14),
                wrap="word"
            )
            textbox.grid(row=0, column=0, sticky="ew", padx=(0, 8))
            textbox.insert("1.0", item)
            textbox.configure(state="disabled")

            copy_icon = self.icons.get("copy")
            copy_button = ctk.CTkButton(
                row,
                text="" if copy_icon else "Kopyala",
                image=copy_icon,
                width=42 if copy_icon else 72,
                height=34,
                corner_radius=10,
                font=("Segoe UI", 12),
                command=lambda value=item: self.copy_to_clipboard(value)
            )
            copy_button.grid(row=0, column=1, sticky="e", padx=(0, 6))

            search_column_width = 42 if self.icons.get("search") else 52
            marketplace_button_width = 72

            if searchable and is_searchable_item(item):
                search_icon = self.icons.get("search")
                search_button = ctk.CTkButton(
                    row,
                    text="" if search_icon else "Ara",
                    image=search_icon,
                    width=search_column_width,
                    height=34,
                    corner_radius=10,
                    font=("Segoe UI", 12),
                    command=lambda query=item: self.search_on_google(query)
                )
                search_button.grid(row=0, column=2, sticky="e", padx=(0, 6))

                marketplace_button = ctk.CTkButton(
                    row,
                    text="Pazar",
                    width=marketplace_button_width,
                    height=34,
                    corner_radius=10,
                    font=("Segoe UI", 12),
                    command=lambda query=item: self.search_on_marketplaces(query)
                )
                marketplace_button.grid(row=0, column=3, sticky="e")
            else:
                search_placeholder = ctk.CTkFrame(
                    row,
                    width=search_column_width,
                    height=34,
                    fg_color="transparent"
                )
                search_placeholder.grid(row=0, column=2, sticky="e", padx=(0, 6))
                search_placeholder.grid_propagate(False)

                marketplace_placeholder = ctk.CTkFrame(
                    row,
                    width=marketplace_button_width,
                    height=34,
                    fg_color="transparent"
                )
                marketplace_placeholder.grid(row=0, column=3, sticky="e")
                marketplace_placeholder.grid_propagate(False)

        bottom_space = ctk.CTkLabel(card, text="", height=8)
        bottom_space.pack()

        return card


if __name__ == "__main__":
    app = HardwareApp()
    app.mainloop()
