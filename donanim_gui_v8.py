import customtkinter as ctk
import wmi
import subprocess
import json
import winreg
import threading
import pythoncom
from datetime import datetime

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


def append_serial(line, serial):
    if not is_valid_value(serial):
        return line

    serial = clean_text(serial)

    if serial.lower() in line.lower():
        return line

    return f"{line} Seri No: {serial}"


def dedupe_items(items):
    seen = set()
    result = []

    for item in items:
        key = item.strip().lower()
        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


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
    c = wmi.WMI()

    try:
        for system in c.Win32_ComputerSystemProduct():
            vendor = clean_text(getattr(system, "Vendor", None))
            name = clean_text(getattr(system, "Name", None))
            version = clean_text(getattr(system, "Version", None))
            serial = getattr(system, "IdentifyingNumber", None)

            line = f"{vendor} {name}"

            if is_valid_value(version) and version.lower() not in line.lower():
                line += f" {version}"

            line = append_serial(line, serial)
            items.append(line)

    except:
        pass

    try:
        for bios in c.Win32_BIOS():
            bios_name = clean_text(getattr(bios, "Name", None))
            bios_version = clean_text(getattr(bios, "SMBIOSBIOSVersion", None))
            bios_serial = getattr(bios, "SerialNumber", None)

            line = f"BIOS: {bios_name}"

            if is_valid_value(bios_version) and bios_version.lower() not in line.lower():
                line += f" {bios_version}"

            line = append_serial(line, bios_serial)
            items.append(line)

    except:
        pass

    if not items:
        items.append("Bilgi bulunamadı.")

    return dedupe_items(items)


def get_cpu_info():
    items = []
    c = wmi.WMI()

    for cpu in c.Win32_Processor():
        items.append(clean_text(cpu.Name))

    return dedupe_items(items)


def get_motherboard_info():
    items = []
    c = wmi.WMI()

    for board in c.Win32_BaseBoard():
        manufacturer = clean_text(board.Manufacturer)
        product = clean_text(board.Product)
        serial = getattr(board, "SerialNumber", None)

        line = f"{manufacturer} {product}"
        line = append_serial(line, serial)

        items.append(line)

    return dedupe_items(items)


def get_gpu_info():
    items = []
    c = wmi.WMI()
    registry_vram = get_gpu_vram_from_registry()

    for gpu in c.Win32_VideoController():
        name = clean_text(gpu.Name)
        vram_gb = bytes_to_gb(gpu.AdapterRAM)

        for reg_name, reg_vram in registry_vram.items():
            if name.lower() in reg_name or reg_name in name.lower():
                vram_gb = reg_vram
                break

        if vram_gb:
            line = f"{name} {vram_gb} GB VRAM"
        else:
            line = f"{name} VRAM bilgisi okunamadı"

        items.append(line)

    return dedupe_items(items)


def get_ram_info():
    items = []
    c = wmi.WMI()

    for ram in c.Win32_PhysicalMemory():
        manufacturer = clean_text(ram.Manufacturer)
        part_number = clean_text(ram.PartNumber)
        serial = getattr(ram, "SerialNumber", None)
        size = bytes_to_gb(ram.Capacity)
        ram_type = memory_type_name(getattr(ram, "SMBIOSMemoryType", None))

        speed = getattr(ram, "ConfiguredClockSpeed", None)
        if not speed:
            speed = getattr(ram, "Speed", None)

        line = f"{manufacturer} {part_number} {ram_type}"

        if speed:
            line += f" {speed} MHz"

        if size:
            line += f" {size} GB"

        line = append_serial(line, serial)
        items.append(line)

    return dedupe_items(items)


def run_powershell_json(command):
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

    command = """
    Get-PhysicalDisk |
    Select-Object FriendlyName, MediaType, Size, SerialNumber |
    ConvertTo-Json
    """

    disks = run_powershell_json(command)

    if disks:
        for disk in disks:
            name = clean_text(disk.get("FriendlyName"))
            media_type = clean_text(disk.get("MediaType"))
            serial = disk.get("SerialNumber")
            size = bytes_to_gb(disk.get("Size"))

            line = f"{name}"

            if size:
                line += f" {size} GB"

            line = append_serial(line, serial)

            if media_type.lower() == "ssd":
                ssd_items.append(line)
            elif media_type.lower() == "hdd":
                hdd_items.append(line)
            else:
                unknown_items.append(f"{line} Tür: {media_type}")

    else:
        c = wmi.WMI()

        for disk in c.Win32_DiskDrive():
            name = clean_text(disk.Model)
            size = bytes_to_gb(disk.Size)
            media_type = clean_text(disk.MediaType)
            serial = getattr(disk, "SerialNumber", None)

            line = f"{name}"

            if size:
                line += f" {size} GB"

            line = append_serial(line, serial)
            unknown_items.append(f"{line} Tür: {media_type}")

    return dedupe_items(ssd_items), dedupe_items(hdd_items), dedupe_items(unknown_items)


def get_battery_info():
    items = []
    c = wmi.WMI()

    for battery in c.Win32_Battery():
        name = clean_text(battery.Name)
        percent = clean_text(getattr(battery, "EstimatedChargeRemaining", None))
        status_code = getattr(battery, "BatteryStatus", None)
        status = battery_status_name(status_code)

        items.append(f"Batarya adı: {name}")
        items.append(f"Batarya durumu: {status}")
        items.append(f"Şarj yüzdesi: %{percent}")

    if not items:
        items.append("Batarya bilgisi bulunamadı. Masaüstü bilgisayarlarda normaldir.")

    return dedupe_items(items)


def get_lhm_power_sensor_info():
    items = []

    try:
        lhm = wmi.WMI(namespace=r"root\LibreHardwareMonitor")
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


class HardwareApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Donanım Bilgi Uygulaması")
        self.geometry("1000x720")
        self.minsize(850, 600)
        self.resizable(True, True)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.main = ctk.CTkFrame(self, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
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

        self.refresh_button = ctk.CTkButton(
            self.sidebar,
            text="Bilgileri Yenile",
            command=self.refresh_data
        )
        self.refresh_button.pack(pady=10, padx=20, fill="x")

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

        self.light_button = ctk.CTkButton(
            self.top_bar,
            text="☀",
            width=38,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 18),
            command=lambda: self.set_theme("light")
        )
        self.light_button.grid(row=0, column=1, padx=(8, 4))

        self.dark_button = ctk.CTkButton(
            self.top_bar,
            text="☾",
            width=38,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 18),
            command=lambda: self.set_theme("dark")
        )
        self.dark_button.grid(row=0, column=2, padx=(4, 0))

        self.content = ctk.CTkScrollableFrame(self.main)
        self.content.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        self.content.grid_columnconfigure(0, weight=1)

        self.refresh_data()

    def set_theme(self, mode):
        ctk.set_appearance_mode(mode)

    def refresh_data(self):
        self.refresh_button.configure(
            text="Yenileniyor...",
            state="disabled"
        )

        self.status_label.configure(
            text="Bilgiler okunuyor..."
        )

        self.clear_content()

        try:
            self.content._parent_canvas.yview_moveto(0)
        except:
            pass

        loading_label = ctk.CTkLabel(
            self.content,
            text="Donanım bilgileri yenileniyor...",
            font=("Segoe UI", 18, "bold")
        )
        loading_label.pack(pady=80)

        thread = threading.Thread(
            target=self.load_data_background,
            daemon=True
        )
        thread.start()

    def load_data_background(self):
        pythoncom.CoInitialize()

        try:
            data = self.collect_all_data()
            self.after(0, lambda data=data: self.update_ui_with_data(data))
        except Exception as error:
            error_message = str(error)
            self.after(0, lambda error_message=error_message: self.show_error(error_message))
        finally:
            pythoncom.CoUninitialize()

    def collect_all_data(self):
        ssd_items, hdd_items, unknown_storage = get_storage_info()

        return {
            "system": get_system_info(),
            "cpu": get_cpu_info(),
            "motherboard": get_motherboard_info(),
            "gpu": get_gpu_info(),
            "ram": get_ram_info(),
            "ssd": ssd_items,
            "hdd": hdd_items,
            "unknown_storage": unknown_storage,
            "battery": get_battery_info(),
            "power_sensors": get_lhm_power_sensor_info()
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

        if data["battery"] and "Batarya bilgisi bulunamadı" not in data["battery"][0]:
            self.add_card("Güç / Batarya", data["battery"])
        else:
            self.add_card("Güç / PSU ve Sensörler", data["power_sensors"])

        now = datetime.now().strftime("%H:%M:%S")

        self.status_label.configure(
            text=f"Son güncelleme: {now}"
        )

        self.refresh_button.configure(
            text="Bilgileri Yenile",
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

        self.refresh_button.configure(
            text="Bilgileri Yenile",
            state="normal"
        )

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def add_card(self, title, items):
        card = ctk.CTkFrame(self.content, corner_radius=18)
        card.pack(fill="x", padx=5, pady=10)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=18, pady=(15, 5))

        textbox = ctk.CTkTextbox(
            card,
            height=max(80, len(items) * 34),
            font=("Consolas", 14),
            wrap="word"
        )
        textbox.pack(fill="x", expand=True, padx=18, pady=(5, 18))

        if items:
            textbox.insert("1.0", "\n".join(items))
        else:
            textbox.insert("1.0", "Bilgi bulunamadı.")

        textbox.configure(state="disabled")


if __name__ == "__main__":
    app = HardwareApp()
    app.mainloop()