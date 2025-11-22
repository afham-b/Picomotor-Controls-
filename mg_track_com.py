import comtypes.client
import time
import os
import subprocess

def open_metaguide():
    # Start MetaGuide
    mg_path = r'C:\Program Files (x86)\MetaGuide.exe'  # Change to the path of your MetaGuide executable
    os.startfile(mg_path)
    time.sleep(10)  # Wait for MetaGuide to open

def load_scope_setup(scope_setup_path):
    # Load scope setup file (.mg)
    #MG = comtypes.client.CreateObject("MetaGuide.Application")
    #MG.LoadScopeSetup(scope_setup_path)
    subprocess.call('C://Users//afham//Documents//MetaGuide/test1.mg')
    time.sleep(5)  # Wait for the setup to load


def main():
    scope_setup_path = r'C:\Users\afham\Documents\MetaGuide\test1.mg'  # Change to the path of your .mg file
    #open_metaguide()
    load_scope_setup(scope_setup_path)
    #lock_star()
    #start_guiding()

if __name__ == "__main__":
    main()
