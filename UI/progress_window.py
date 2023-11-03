from PySide6 import QtWidgets
from UI.ui_progress_form import Ui_ProgressWindow

from mod_generator import ModsProcess

import os
import copy
import shutil



class ProgressWindow(QtWidgets.QMainWindow):
    
    def __init__(self, rom_path, out_dir, seed, settings):
        super (ProgressWindow, self).__init__()
        self.ui = Ui_ProgressWindow()
        self.ui.setupUi(self)
        
        self.rom_path : str = rom_path
        self.out_dir : str = out_dir
        self.seed : str = seed
        self.settings = copy.deepcopy(settings)
        
        self.num_of_mod_tasks = 85
        if self.settings['kettles']:
            self.num_of_mod_tasks += 69
        
        self.done = False
        self.cancel = False

        self.mods_error = False
        self.mods_done = False
        
        if os.path.exists(self.out_dir): # remove old mod files if generating a new one with the same seed
            shutil.rmtree(self.out_dir, ignore_errors=True)
        
        self.ui.progressBar.setMaximum(self.num_of_mod_tasks)
        self.mods_process = ModsProcess(self.rom_path, f'{self.out_dir}', self.seed, self.settings)
        self.mods_process.setParent(self)
        self.mods_process.progress_update.connect(self.updateProgress)
        self.mods_process.status_update.connect(self.updateStatus)
        self.mods_process.error.connect(self.modsError)
        self.mods_process.is_done.connect(self.modsDone)
        self.mods_process.start() # start the modgenerator
    

    # receives the int signal as a parameter named progress
    def updateProgress(self, progress):
        self.ui.progressBar.setValue(progress)
    

    # receives the string signal as a parameter named status
    def updateStatus(self, status):
        self.ui.label.setText(status)
    

    def modsError(self, er_message=str):
        self.mods_error = True
        from randomizer_paths import LOGS_PATH
        with open(LOGS_PATH, 'w') as f:
            f.write(f'{self.seed}')
            f.write(f'\n\n{er_message}')
    

    def modsDone(self):
        if self.mods_error:
            self.ui.label.setText("Error detected! Check the created log.txt for more info")
            if os.path.exists(self.out_dir): # delete files if user canceled
                shutil.rmtree(self.out_dir, ignore_errors=True)
            self.done = True
            return
        
        if self.cancel:
            self.ui.label.setText("Canceling...")
            if os.path.exists(self.out_dir): # delete files if user canceled
                shutil.rmtree(self.out_dir, ignore_errors=True)
            self.done = True
            self.close()
            return
        
        self.ui.progressBar.setValue(self.num_of_mod_tasks)
        self.ui.label.setText("All done! Check the README for instructions on how to play!")
        self.done = True


    # override the window close event to close the randomization thread
    def closeEvent(self, event):
        if self.done:
            event.accept()
        else:
            event.ignore()
            self.cancel = True
            self.ui.label.setText('Canceling...')
            self.mods_process.stop()
