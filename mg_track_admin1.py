# trying to run as admin

import subprocess
import sys
import ctypes

def run_as_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        else:
            print("Already running with administrative privileges.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    try:
        # Example: Start MetaGuide.exe with elevated privileges
        subprocess.Popen(["runas", "/user:Administrator", "C:\\Program Files (x86)\\MetaGuide\\MetaGuide.exe"])
        print("MetaGuide started with admin privileges.")
    except Exception as e:
        print(f"Error starting MetaGuide: {e}")

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Re-launching script with admin privileges.")
        run_as_admin()
    else:
        main()
