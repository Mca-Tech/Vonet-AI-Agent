# /core/system_utils.py

import subprocess
import threading
import time
import os
import platform
import socket
import uuid
import psutil
import datetime
import wmi
import pythoncom
import config
from . import memory_manager

def get_static_info():
    pythoncom.CoInitialize()  # Initialize COM for thread safety
    try:
        c = wmi.WMI()
        os_info = c.Win32_OperatingSystem()[0]
        baseboard = c.Win32_BaseBoard()[0]
        processor = c.Win32_Processor()[0]
        gpu = c.Win32_VideoController()[0]
        physical_memory = sum([int(mem.Capacity) for mem in c.Win32_PhysicalMemory()])
        disk_count = len(c.Win32_DiskDrive())

        static_info = {
            "PC_Name": platform.node(),
            "OS": os_info.Caption.strip(),
            "OS_Version": os_info.Version,
            "CPU": processor.Name.strip(),
            "CPU_Cores": psutil.cpu_count(logical=False),
            "GPU": gpu.Name.strip(),
            "RAM_GB": round(physical_memory / (1024 ** 3), 2),
            "System_Drive_Type": "SSD" if "SSD" in c.Win32_DiskDrive()[0].MediaType else "HDD",
            "Total_Drives": disk_count,
            "MAC_Address": ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1]),
            "Motherboard": baseboard.Product,
            "Architecture": platform.architecture()[0],
            "First_Use_Date": os_info.InstallDate.split('.')[0]
        }

        with open(config.resource_path("assets/system_static_info.txt"), 'w') as f:
            f.write("[SYSTEM INFO]\n")
            for key, value in static_info.items():
                f.write(f"{key}: {value}\n")

    finally:
        pythoncom.CoUninitialize()

def get_dynamic_info():
    pythoncom.CoInitialize()
    try:
        partitions = psutil.disk_partitions()
        disk_usage = {}
        for part in partitions:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_usage[part.device] = f"{usage.percent}%"
            except PermissionError:
                continue

        services = []
        try:
            c = wmi.WMI()
            services = [s.Name for s in c.Win32_Service() if s.State == "Running"]
        except:
            services = []

        status = 'Disconnected'
        adapter = "Unknown"
        stats = psutil.net_if_stats()
        for nic, nic_stats in stats.items():
            if nic_stats.isup:
                status = "Connected"
                adapter = nic
                break

        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat()
        try:
            hostname = socket.gethostbyname(socket.gethostname())
        except:
            hostname = "Unavailable"

        dynamic_info = {
            "Last_Boot": boot_time,
            "CPU_Usage_Avg": round(psutil.cpu_percent(interval=1), 2),
            "RAM_Usage_Avg": round(psutil.virtual_memory().percent, 2),
            "Running_Processes_Count": len(psutil.pids()),
            "Network_Status": status,
            "IP_Address": hostname,
            "Active_Network_Adapter": adapter
        }

        with open(config.resource_path("assets/system_dynamic_info.txt"), 'w') as f:
            f.write("[SYSTEM INFO]\n")
            for key, value in dynamic_info.items():
                f.write(f"{key}: {value}\n")

            f.write("\n[Disk Usage]\n")
            for disk, percent in disk_usage.items():
                f.write(f"{disk}: {percent}\n")

            f.write("\n[Running Services]\n")
            for service in services:
                f.write(f"{service}\n")

    finally:
        pythoncom.CoUninitialize()

def run_background_command(command):
    """Runs a PowerShell command in the background and monitors its output."""
    if "VONET list --tasks" in command:
        config.SYSTEM_MESSAGE_FOR_AI = str(config.processes)
        return

    if command.startswith("VONET_MEMORY_UPDATE"):
        try:
            parts = command.split()
            key_index = parts.index("--key") + 1
            value_index = parts.index("--value") + 1
            key = parts[key_index]
            value = " ".join(parts[value_index:])

            if key == "UserName":
                config.vonet_memory_data['user_info']['name'] = value
                memory_manager.save_memory()
                print(f"Memory updated: UserName set to {value}")
            else:
                config.SYSTEM_MESSAGE_FOR_AI = f"Error: Unknown memory key '{key}'."
        except (ValueError, IndexError) as e:
            config.SYSTEM_MESSAGE_FOR_AI = f"Error: Invalid format for VONET_MEMORY_UPDATE. Expected '--key <key> --value <value>'. Error: {e}"
        
        if config.app_instance:
            config.app_instance.after(0, config.app_instance.loading, "end")
        return

    pws_script = config.resource_path(r"pws_script\powershell_command.ps1")
    os.makedirs(os.path.dirname(pws_script), exist_ok=True)
    with open(pws_script, 'w') as ps1_file:
        ps1_file.write(command)

    proc = subprocess.Popen(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", pws_script],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True, bufsize=1
    )

    log = []
    task_name = proc.pid
    config.processes[task_name] = {
        "process": proc, "log": log, "status": "running",
        "exit_code": None, "command": command
    }

    def reader():
        for line in proc.stdout:
            log.append(line.rstrip())

    def monitor_finished():
        proc.wait()
        if config.app_instance:
            config.app_instance.after(0, config.app_instance.loading, "end", "")

        exit_code = proc.returncode
        if task_name in config.processes:
            status = "success" if exit_code == 0 else "failed"
            config.processes[task_name]["status"] = status
            config.processes[task_name]["exit_code"] = exit_code
            
            final_log = "\n".join(config.processes[task_name]["log"])
            if not final_log.strip():
                final_log = "Command executed successfully with no output." if status == "success" else f"Command failed with exit code {exit_code} and no output."
            
            print(f"Command finished with output:\n{final_log}")
            config.SYSTEM_MESSAGE_FOR_AI = final_log
            
            # Clean up the finished process entry after a delay
            time.sleep(10)
            if task_name in config.processes:
                del config.processes[task_name]

    threading.Thread(target=reader, daemon=True).start()
    threading.Thread(target=monitor_finished, daemon=True).start()