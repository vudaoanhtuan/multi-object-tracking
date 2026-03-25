from mot_va.views.main_window import MainWindow


def create_main_window() -> MainWindow:
    window = MainWindow()
    window.setWindowTitle("MOT Visualization & Annotation")
    window.resize(1400, 900)
    return window
