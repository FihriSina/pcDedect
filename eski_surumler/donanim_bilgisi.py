import wmi

c = wmi.WMI()

print("=== İşlemci ===")
for cpu in c.Win32_Processor():
    print(cpu.Name)

print("\n=== Anakart ===")
for board in c.Win32_BaseBoard():
    print(f"{board.Manufacturer} {board.Product}")

print("\n=== Ekran Kartı ===")
for gpu in c.Win32_VideoController():
    print(gpu.Name)

print("\n=== RAM ===")
for ram in c.Win32_PhysicalMemory():
    capacity_gb = int(ram.Capacity) / (1024 ** 3)
    print(f"{ram.Manufacturer} {ram.PartNumber} - {capacity_gb:.0f} GB")

print("\n=== Diskler SSD / HDD ===")
for disk in c.Win32_DiskDrive():
    size_gb = int(disk.Size) / (1024 ** 3)
    print(f"{disk.Model} - {size_gb:.0f} GB - {disk.MediaType}")

print("\n=== Güç / Batarya ===")
for battery in c.Win32_Battery():
    print(f"{battery.Name} - Durum: {battery.BatteryStatus}")