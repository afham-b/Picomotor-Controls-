import win32com.client
import time
import os
import pythoncom
import win32api
import win32con

def open_metaguide():
    # Start MetaGuide
    mg_path = r'C:\Program Files (x86)\MetaGuide.exe'  # Change to the path of your MetaGuide executable
    os.startfile(mg_path)
    time.sleep(10)  # Wait for MetaGuide to open

def load_scope_setup(scope_setup_path):
    # Load scope setup file (.mg)
    MG = win32com.client.Dispatch("MetaGuide.Application")
    MG.LoadScopeSetup(scope_setup_path)
    time.sleep(5)  # Wait for the setup to load

def lock_star():
    MG = win32com.client.Dispatch("MetaGuide.Application")
    MG.LockStar()
    time.sleep(2)  # Wait for the star to lock

def start_guiding():
    MG = win32com.client.Dispatch("MetaGuide.Application")
    MG.StartGuiding()
    print("Guiding started")

def main():
    scope_setup_path = r'C:\Users\afham\Documents\MetaGuide\test1.mg'  # Change to the path of your .mg file
    #open_metaguide()
    load_scope_setup(scope_setup_path)
    #lock_star()
    #start_guiding()

if __name__ == "__main__":
    main()
