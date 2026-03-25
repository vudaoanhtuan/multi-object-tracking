import sys

from PyQt6.QtWidgets import QApplication

from mot_va.app import create_main_window


def main() -> None:
    app = QApplication(sys.argv)
    window = create_main_window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
