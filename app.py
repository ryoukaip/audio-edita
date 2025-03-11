import sys
from PyQt5.QtWidgets import QApplication
from main_screen import AudioEditorUI
from welcome import WelcomeWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    main_window = AudioEditorUI()
    main_window.setWindowOpacity(0.0)
    main_window.show()

    welcome = WelcomeWindow(main_window)
    welcome.show()
    
    sys.exit(app.exec_())