import json
import customtkinter as CTk
from tkinter import messagebox
import psutil
from platform import uname


base_padding = {'padx': 10, 'pady': 8}
office = None


class Enter_Office():
    def __init__(self):
        self.window = CTk.CTk()
        self.window.title('Coolect system info')
        self.window.geometry('325x130')
        self.window.resizable(False, False)
        CTk.set_appearance_mode("dark")
        CTk.set_default_color_theme("dark-blue")
        self.open_window()

    def open_window(self):
        self.office_label = CTk.CTkLabel(self.window, font=CTk.CTkFont(size=20, weight="bold"), text='Номер кабинета', **base_padding)
        self.office_label.pack()
        self.office_entry = CTk.CTkEntry(self.window)
        self.office_entry.pack()
        self.office_btn = CTk.CTkButton(self.window, text='Экспортировать system info', font=CTk.CTkFont(size=20, weight="bold"), command=self.save_office)
        self.office_btn.pack(**base_padding)
        self.window.mainloop()

    def save_office(self):
        global office
        office = self.office_entry.get()
        main()


def correct_size(bts, ending='iB'):
    size = 1024
    for item in ["", "K", "M", "G", "T", "P"]:
        if bts < size:
            return f"{bts:.2f}{item}{ending}"
        bts /= size


def creating_file():
    collect_info_dict = dict()
    if 'info' not in collect_info_dict:
        collect_info_dict['info'] = dict()
        collect_info_dict['info']['system_info'] = dict()
        collect_info_dict['info']['system_info'] = {'system': {'comp_name': uname().node,
                                                            'os_name': f"{uname().system} {uname().release}",
                                                            'version': uname().version,
                                                            'machine': uname().machine},
                                                    'processor': {'name': uname().processor,
                                                                'phisycal_core': psutil.cpu_count(logical=False),
                                                                'all_core': psutil.cpu_count(logical=True),
                                                                'freq_max': f"{psutil.cpu_freq().max:.2f}Мгц"},
                                                    'ram': {'volume': correct_size(psutil.virtual_memory().total),
                                                            'aviable': correct_size(psutil.virtual_memory().available),
                                                            'used': correct_size(psutil.virtual_memory().used)}}

    for partition in psutil.disk_partitions():
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        if 'disk_info' not in collect_info_dict['info']:
            collect_info_dict['info']['disk_info'] = dict()
        if f"'device': {partition.device}" not in collect_info_dict['info']['disk_info']:
            collect_info_dict['info']['disk_info'][partition.device] = dict()
            collect_info_dict['info']['disk_info'][partition.device] = {'file_system': partition.fstype,
                                                                        'size_total': correct_size(
                                                                            partition_usage.total),
                                                                        'size_used': correct_size(
                                                                            partition_usage.used),
                                                                        'size_free': correct_size(
                                                                            partition_usage.free),
                                                                        'percent':
                                                                            f'{partition_usage.percent}'}

    for interface_name, interface_address in psutil.net_if_addrs().items():
        if interface_name == 'Loopback Pseudo-Interface 1':
            continue
        else:
            if 'net_info' not in collect_info_dict['info']:
                collect_info_dict['info']['net_info'] = dict()
            if interface_name not in collect_info_dict['info']['net_info']:
                collect_info_dict['info']['net_info'][interface_name] = dict()
                collect_info_dict['info']['net_info'][interface_name] = {
                    'mac': interface_address[0].address.replace("-", ":"),
                    'ipv4': interface_address[1].address,
                    'ipv6': interface_address[2].address}

    return collect_info_dict


def save_txt(dict_info):
    file = open(f'./Users_system_info/{office}_{uname().node}.txt', 'a')
    for item in dict_info['info']:
        if item == "system_info":
            for elem in dict_info['info'][item]:
                if elem == 'system':
                    file.write(f"[+] Информация о системе\n"
                        f"\t- Имя компьютера: {dict_info['info'][item][elem]['comp_name']}\n"
                        f"\t- Опереционная система: {dict_info['info'][item][elem]['os_name']}\n"
                        f"\t- Сборка: {dict_info['info'][item][elem]['version']}\n"
                        f"\t- Архитектура: {dict_info['info'][item][elem]['machine']}\n")
                if elem == 'processor':
                    file.write(f"[+] Информация о процессоре\n"
                        f"\t- Семейство: {dict_info['info'][item][elem]['name']}\n"
                        f"\t- Физические ядра: {dict_info['info'][item][elem]['phisycal_core']}\n"
                        f"\t- Всего ядер: {dict_info['info'][item][elem]['all_core']}\n"
                        f"\t- Максимальная частота: {dict_info['info'][item][elem]['freq_max']}\n")
                if elem == 'ram':
                    file.write(f"[+] Оперативная память\n"
                        f"\t- Объем: {dict_info['info'][item][elem]['volume']}\n"
                        f"\t- Доступно: {dict_info['info'][item][elem]['aviable']}\n"
                        f"\t- Используется: {dict_info['info'][item][elem]['used']}\n")
        if item == "disk_info":
            for elem in dict_info['info'][item]:
                file.write(f"[+] Информация о дисках\n"
                    f"\t- Имя диска: {elem}\n"
                    f"\t- Файловая система: {dict_info['info'][item][elem]['file_system']}\n"
                    f"\t- Объем диска: {dict_info['info'][item][elem]['size_total']}\n"
                    f"\t- Занято: {dict_info['info'][item][elem]['size_used']}\n"
                    f"\t- Свободно: {dict_info['info'][item][elem]['size_free']}\n"
                    f"\t- Заполненность: {dict_info['info'][item][elem]['percent']}%\n")
        if item == "net_info":
            for elem in dict_info['info'][item]:
                file.write(f"[+] Информация о сети\n"
                    f"\t- Имя интерфейса: {elem}\n"
                    f"\t- MAC-адрес: {dict_info['info'][item][elem]['mac']}\n"
                    f"\t- IPv4: {dict_info['info'][item][elem]['ipv4']}\n"
                    f"\t- IPv6: {dict_info['info'][item][elem]['ipv6']}\n")

def main():
    if uname().system == "Windows":
        dict_info = creating_file()
        with open(f'info_{uname().node}.json', 'w', encoding='utf-8') as file:
            json.dump(dict_info, file, indent=4, ensure_ascii=False)
        try: 
            save_txt(dict_info)
            messagebox.showinfo('Успешно', 'Конфигурация системы экспортированна в папку Users_system_info')
        except: messagebox.showerror('Ошибка', 'Ошибка записи файла')
    elif uname().system == "Linux":
        dict_info = creating_file()
        with open(f'info_{uname().node}.json', 'w', encoding='utf-8') as file:
            json.dump(dict_info, file, indent=4, ensure_ascii=False)
        save_txt(dict_info)


if __name__ == "__main__":
    Enter_Office()

