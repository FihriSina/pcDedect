import customtkinter as ctk
import wmi

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

c = wmi.WMI()


def gb(value):
    try:
        return round(int(value) / (1024 ** 3), 2)
    except:
        return "Bilinmiyor"


def get_hardware_info():
    info = {
        "cpu": [],
        "motherboard": [],
        "gpu": [],
        "ram": [],
        "ssd": [],
        "hdd": [],
        "battery": []
    }

    for cpu in c.Win32_Processor():
        info["cpu"].append(cpu.Name)

    for board in c.Win32_BaseBoard():
        info["motherboard"].append(
            f"{board.Manufacturer} {board.Product}"
        )

    for gpu in c.Win32_VideoController():
        vram = gb(gpu.AdapterRAM)
        info["gpu"].append(
            f"{gpu.Name}\nVRAM: {vram} GB"
        )

    for ram in c.Win32_PhysicalMemory():
        size = gb(ram.Capacity)
        info["ram"].append(
            f"{ram.Manufacturer} {ram.PartNumber} - {size} GB"
        )

    for disk in c.Win32_DiskDrive():
        model = disk.Model
        size = gb(disk.Size)
        media_type = str(disk.MediaType).lower()

        text = f"{model} - {size} GB"

        if "ssd" in media_type:
            info["ssd"].append(text)
        elif "hdd" in media_type or "fixed" in media_type:
            info["hdd"].append(text)
        else:
            info["hdd"].append(text)

    for battery in c.Win32_Battery():
        info["battery"].append(
            f"{battery.Name} - Durum Kodu: {battery.BatteryStatus}"
        )

    return info


class HardwareApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Donanım Bilgi Uygulaması")
        self.geometry("850x650")
        self.resizable(False, False)

        title = ctk.CTkLabel(
            self,
            text="Bilgisayar Donanım Bilgileri",
            font=("Arial", 26, "bold")
        )
        title.pack(pady=20)

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=780,
            height=540
        )
        self.scroll_frame.pack(pady=10)

        self.load_data()

    def add_section(self, title, items):
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", padx=15, pady=10)

        label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 18, "bold"),
            anchor="w"
        )
        label.pack(fill="x", padx=15, pady=(10, 5))

        if items:
            for item in items:
                item_label = ctk.CTkLabel(
                    frame,
                    text=item,
                    font=("Arial", 14),
                    anchor="w",
                    justify="left"
                )
                item_label.pack(fill="x", padx=20, pady=4)
        else:
            empty_label = ctk.CTkLabel(
                frame,
                text="Bilgi bulunamadı.",
                font=("Arial", 14),
                anchor="w"
            )
            empty_label.pack(fill="x", padx=20, pady=4)

    def load_data(self):
        data = get_hardware_info()

        self.add_section("İşlemci", data["cpu"])
        self.add_section("Anakart", data["motherboard"])
        self.add_section("Ekran Kartı / VRAM", data["gpu"])
        self.add_section("RAM", data["ram"])

        self.add_section("Depolama - SSD", data["ssd"])
        self.add_section("Depolama - HDD", data["hdd"])

        self.add_section("Güç - Batarya", data["battery"])
        self.add_section(
            "Güç - PSU",
            [
                "Masaüstü bilgisayarlarda PSU marka/model bilgisi genellikle yazılımsal olarak okunamaz.",
                "Bu bilgi çoğu zaman yalnızca güç kaynağı üzerindeki etiketten öğrenilebilir."
            ]
        )


if __name__ == "__main__":
    app = HardwareApp()
    app.mainloop()