import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ứng dụng PyQt5 với QMainWindow")
        self.setGeometry(100, 100, 600, 400)

        # Thêm widget chính (ví dụ: QLabel)
        label = QLabel("Chào mừng bạn đến với PyQt5!", self)
        label.setGeometry(200, 150, 250, 50)

        # Thêm thanh trạng thái
        self.statusBar().showMessage("Sẵn sàng")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
