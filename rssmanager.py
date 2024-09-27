import sys
import psutil
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel,
                             QSystemTrayIcon, QMenu, QStyle, QTabWidget, QScrollArea)
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QAction, QIcon

class ResourceMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_system_tray()
        self.init_timer()

    def init_ui(self):
        self.setWindowTitle('PC Resource Monitor')
        self.setGeometry(100, 100, 400, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        # Overview Tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        self.cpu_label, self.cpu_bar = self.create_resource_widgets("CPU Usage:")
        self.mem_label, self.mem_bar = self.create_resource_widgets("Memory Usage:")
        self.disk_label, self.disk_bar = self.create_resource_widgets("Disk Usage:")
        
        for widget in (self.cpu_label, self.cpu_bar, self.mem_label, self.mem_bar, 
                       self.disk_label, self.disk_bar):
            overview_layout.addWidget(widget)
        
        overview_tab.setLayout(overview_layout)
        self.tabs.addTab(overview_tab, "Overview")

        # CPU Tab
        cpu_tab = QWidget()
        cpu_layout = QVBoxLayout()
        self.cpu_cores_layout = QVBoxLayout()
        cpu_scroll = QScrollArea()
        cpu_scroll.setWidgetResizable(True)
        cpu_scroll_content = QWidget()
        cpu_scroll_content.setLayout(self.cpu_cores_layout)
        cpu_scroll.setWidget(cpu_scroll_content)
        cpu_layout.addWidget(cpu_scroll)
        cpu_tab.setLayout(cpu_layout)
        self.tabs.addTab(cpu_tab, "CPU")

        # Memory Tab
        mem_tab = QWidget()
        mem_layout = QVBoxLayout()
        self.mem_sticks_layout = QVBoxLayout()
        mem_scroll = QScrollArea()
        mem_scroll.setWidgetResizable(True)
        mem_scroll_content = QWidget()
        mem_scroll_content.setLayout(self.mem_sticks_layout)
        mem_scroll.setWidget(mem_scroll_content)
        mem_layout.addWidget(mem_scroll)
        mem_tab.setLayout(mem_layout)
        self.tabs.addTab(mem_tab, "Memory")

        # System Info Tab
        sysinfo_tab = QWidget()
        sysinfo_layout = QVBoxLayout()
        self.sysinfo_label = QLabel()
        sysinfo_layout.addWidget(self.sysinfo_label)
        sysinfo_tab.setLayout(sysinfo_layout)
        self.tabs.addTab(sysinfo_tab, "System Info")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        self.apply_styles()

    def create_resource_widgets(self, label_text):
        label = QLabel(label_text)
        bar = QProgressBar()
        return label, bar

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                border-radius: 10px;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 20px;
            }
            QTabWidget::pane {
                border: 1px solid #76797C;
                background-color: transparent;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #F0F0F0;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background-color: #05B8CC;
            }
            QScrollArea {
                border: none;
            }
        """)

    def init_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))

        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Exit", self)

        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(QApplication.instance().quit)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def init_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every 1 second

    def update_stats(self):
        try:
            # Overview
            self.update_resource(self.cpu_label, self.cpu_bar, psutil.cpu_percent(), "CPU Usage")
            self.update_resource(self.mem_label, self.mem_bar, psutil.virtual_memory().percent, "Memory Usage")
            self.update_resource(self.disk_label, self.disk_bar, psutil.disk_usage('/').percent, "Disk Usage")

            # CPU Cores
            cpu_percent = psutil.cpu_percent(percpu=True)
            for i, percent in enumerate(cpu_percent):
                if i >= self.cpu_cores_layout.count() // 2:
                    label = QLabel(f"Core {i}:")
                    bar = QProgressBar()
                    self.cpu_cores_layout.addWidget(label)
                    self.cpu_cores_layout.addWidget(bar)
                else:
                    label = self.cpu_cores_layout.itemAt(i*2).widget()
                    bar = self.cpu_cores_layout.itemAt(i*2+1).widget()
                self.update_resource(label, bar, percent, f"Core {i}")

            # Memory Sticks (simplified)
            mem_info = psutil.virtual_memory()
            total_memory = mem_info.total
            used_memory = mem_info.used
            stick_size = 8 * 1024 * 1024 * 1024  # 8GB
            num_sticks = total_memory // stick_size + (1 if total_memory % stick_size else 0)
            
            for i in range(num_sticks):
                if i >= self.mem_sticks_layout.count() // 2:
                    label = QLabel(f"RAM Stick {i}:")
                    bar = QProgressBar()
                    self.mem_sticks_layout.addWidget(label)
                    self.mem_sticks_layout.addWidget(bar)
                else:
                    label = self.mem_sticks_layout.itemAt(i*2).widget()
                    bar = self.mem_sticks_layout.itemAt(i*2+1).widget()
                stick_usage = min(100, (used_memory / stick_size) * 100)
                self.update_resource(label, bar, stick_usage, f"RAM Stick {i}")
                used_memory = max(0, used_memory - stick_size)

            # System Info
            system_info = f"""
            OS: {sys.platform}
            CPU: {psutil.cpu_count(logical=False)} physical cores, {psutil.cpu_count(logical=True)} logical cores
            RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB
            """
            self.sysinfo_label.setText(system_info)

        except Exception as e:
            print(f"Error updating stats: {e}")

    def update_resource(self, label, bar, value, resource_name):
        bar.setValue(int(value))
        label.setText(f'{resource_name}: {value:.1f}%')

    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPosition().toPoint()

def main():
    app = QApplication(sys.argv)
    
    if sys.platform == "win32":
        import ctypes
        myappid = 'com.yourcompany.resourcemonitor.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app.setWindowIcon(QIcon('icon.ico'))  # Make sure to have an icon.ico file in the same directory
    
    monitor = ResourceMonitor()
    monitor.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
