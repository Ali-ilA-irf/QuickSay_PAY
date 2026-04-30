import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback
import customtkinter as ctk

try:
    ctk.set_appearance_mode('dark')
    root = ctk.CTk()
    from gui.views.teller.teller_main import TellerDashboard
    user_data = {'USERNAME': 'teller_alice', 'ROLE': 'TELLER', 'BRANCH_CODE': 'QSB0000001'}
    print('Trying to instantiate TellerDashboard...')
    TellerDashboard(root, user_data, lambda: None)
    print("Success")
except Exception as e:
    traceback.print_exc()
