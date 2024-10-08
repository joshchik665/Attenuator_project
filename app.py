import sys
import json

from instruments.J7204B import J7204B

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QTabWidget,
    QStatusBar,
    QFileDialog,
)


class MainWindow(QMainWindow):
    """Class for the main window"""
    def __init__(self):
        super().__init__()
        
        # Sets Title of the window and the icon
        self.setWindowTitle(' ')
        my_icon = QIcon()
        my_icon.addFile('icon\\crc_icon.ico')
        self.setWindowIcon(my_icon)
        
        self.start_page()
    
    
    def start_page(self):
        """Sets up the tabs and launchs the first window"""
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.clicked.connect(self.add_new_tab)
        
        self.tab_bar_layout = QHBoxLayout()
        self.tab_bar_layout.addWidget(self.new_tab_button)
        self.tab_widget.setCornerWidget(self.new_tab_button, corner=Qt.BottomRightCorner)
        
        self.add_new_tab()  # Add the first tab initially
    
    
    @Slot()
    def add_new_tab(self):
        """Opens new tab"""
        new_tab = DeviceTab() # Creates new tab object
        new_tab.set_stylesheet()
        tab_index = self.tab_widget.addTab(new_tab, f"Device {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(tab_index)


class DeviceTab(QWidget):
    """Object containing everyting on the tab"""
    def __init__(self):
        super().__init__()
        
        self.devices_settings = {
            'Keysight_J7204B': ['Ch.1','Ch.2','Ch.3','Ch.4'],
        } # library containing a list of each channel in each instrument type
        
        self.channel_widgets = {} # Library that holds all the widgets for each channel
        
        # Sets initial status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage('Not Connected!',timeout=0)
        
        self.connected=False
        
        self.start_page()
    
    
    def start_page(self):
        # Creats Title widget
        title = QLabel("Lab Attenuator GUI")
        font = title.font()
        font.setPointSize(30)
        font.setBold(True)
        title.setFont(font)
        
        # IP entry widgets
        ip_entry_lable = QLabel('Enter IP Address:')
        
        self.ip_entry = QLineEdit()
        self.ip_entry.setInputMask('000.000.000.000;_')
        self.ip_entry.setFixedWidth(85)
        self.ip_entry.returnPressed.connect(self.connect_device)
        
        self.connect_button = QPushButton('Connect')
        self.connect_button.pressed.connect(self.connect_device)
        
        # Save and Load config buttons
        self.save_button = QPushButton('Save Config')
        self.save_button.pressed.connect(self.save_settings)
        self.save_button.setDisabled(True)
        
        self.load_button = QPushButton('load Config')
        self.load_button.pressed.connect(self.load_settings)
        
        # CRC logo image
        img= QImage('icon\\crc_icon.png')
        pixmap = QPixmap(img.scaledToWidth(100))
        crc_logo = QLabel(self)
        crc_logo.setPixmap(pixmap)
        crc_logo.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        # Sets Layout for the window
        ip_entry_layout = QHBoxLayout()
        ip_entry_layout.addWidget(self.ip_entry)
        ip_entry_layout.addWidget(self.connect_button)
        ip_entry_layout.addWidget(self.save_button)
        ip_entry_layout.addWidget(self.load_button)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(ip_entry_lable)
        title_layout.addLayout(ip_entry_layout)
        
        header_layout = QHBoxLayout()
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(crc_logo)
        
        self.channel_layout = QHBoxLayout()
        
        self.window_layout = QVBoxLayout()
        self.window_layout.addLayout(header_layout)
        self.window_layout.addLayout(self.channel_layout)
        self.window_layout.addWidget(self.status_bar)
        
        self.setLayout(self.window_layout)
    
    
    def connect_device(self):
        """reads value in box and then calls the rest of the function"""
        self.ip_address = self.ip_entry.text()
        self._connect_device()
    
    
    def _connect_device(self):
        """Attempts to connect to the device and creates the channel widgets for device"""
        self.device = J7204B(self.ip_address)
        self.connected = self.device.connected
        
        # if connected to instrument
        if self.device.connected:
            self.channels = self.devices_settings[self.device.device_type] # Gets the chanels for the device type
            
            # for all the channels for the device, create and object and attach the correct function
            for channel_name in self.channels:
                self.channel_widgets[channel_name] = ChannelWidget(channel_name)
                
                def make_callback(param):
                    return lambda: self.set_value(param)
                
                callback_function = make_callback(channel_name)
                
                self.channel_widgets[channel_name].entry_box.valueChanged.connect(callback_function)
            
            # Place the channel widgets
            for __,value in self.channel_widgets.items():
                self.channel_layout.addWidget(value)
            
            # Update status bar
            self.status_bar.showMessage('Connected to: ' + self.device.device_type + ' @' + self.ip_address,timeout=0)
            
            self.update_values() # Check values and update them
            
            # disable ip entry box and button, enable save button
            self.ip_entry.setDisabled(True)
            self.connect_button.setDisabled(True)
            self.save_button.setDisabled(False)
        else:
            self.fail_connect_msg()
    
    
    def update_values(self):
        """for each channel, call update_value()"""
        for key, value in self.channel_widgets.items():
            self.update_value(key,value)
            value.entry_box.setDisabled(False)
    
    
    def update_value(self, channel_name, channel_widget):
        """Get the current value, set the current value to the display"""
        self.device.get_channel_value(channel_name)
        channel_widget.entry_box.setValue(self.device.channel_values[channel_name])
    
    
    def set_value(self, channel_name):
        """Set a value from the entry box to the device and validate it"""
        value = self.channel_widgets[channel_name].entry_box.value() # get value
        self.device.set_channel_value(channel_name,value) # Set the value on the device
        self.update_value(channel_name,self.channel_widgets[channel_name]) # get new value and set it on the display
        
        # if the current value is different from the one that we wanted, color text red, otherwise green
        if not value == self.device.channel_values[channel_name]:
            self.channel_widgets[channel_name].entry_box.setStyleSheet("QSpinBox { color: red; }")
        else:
            self.channel_widgets[channel_name].entry_box.setStyleSheet("QSpinBox { color: green; }")
    
    
    def fail_connect_msg(self):
        # Create a QMessageBox instance
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Invalid IP address OR device could not be found!")
        msg.setWindowTitle("Message")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    
    def wrong_config(self):
        # Create a QMessageBox instance
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("The selected config is not for current device")
        msg.setWindowTitle("Message")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    
    def invalid_filetype(self):
        # Create a QMessageBox instance
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Invalid File Type!")
        msg.setWindowTitle("Message")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    
    def set_stylesheet(self):
        # Define the stylesheet with border-radius for QPushButton and QLineEdit
        stylesheet = """
            QPushButton {
                border-radius: 10px;
                padding: 5px;
                border: 1px solid #8f8f91;
                background-color: #2596be;
                color: white;
            }
            QPushButton:pressed {
                background-color: darkblue;
                border-style: inset
            }
            QPushButton:disabled {
                background-color: darkgray;
            }
            QLineEdit {
                border-radius: 10px;
                padding: 5px;
                border: 1px solid #8f8f91;
            }
            QLineEdit:disabled {
                background-color: lightgray;
            }
            QSpinBox {
                font-size: 24px;
                border: 1px solid #8f8f91;
                padding: 2px;
                border-radius: 5px;
            }
        """
        # Apply the stylesheet to the application
        self.setStyleSheet(stylesheet)
    
    
    def save_file_dialog(self):
        # Create and configure the file dialog
        file_path, _ = QFileDialog.getSaveFileName(self, 'Create or overwrite .json file', '', 'JSON Files (*.json)')

        if file_path:
            if not file_path.endswith('.json'):  # Ensure the file has a .json extension
                file_path += '.json'
            return file_path
        return 0
    
    
    def open_file_dialog(self):
        file_path, __ = QFileDialog.getOpenFileName(self,'Open .json file','','JSON Files (*.json)')
        
        if not file_path:
            return 0
        if not file_path.endswith('.json'):
            self.invalid_filetype()
            return 0
        else:
            return file_path
    
    
    def save_settings(self):
        config = {}
        config['device_type'] = self.device.device_type
        config['ip_address'] = self.ip_address
        config['channels'] = {}
        for key,value in self.channel_widgets.items():
            config['channels'][key] = {
                'channel_label': value.channel_label,
                'channel_value': value.entry_box.value(),
            }
        
        with open(self.save_file_dialog(), 'w') as file:
            json.dump(config, file)
    
    
    def load_settings(self):
        with open(self.open_file_dialog(), 'r') as file:
            config = json.load(file)
        
        if not self.connected:
            self.ip_address = config['ip_address']
            self._connect_device()
        
        if not self.device.device_type == config['device_type']:
            self.wrong_config()
        else:
            for key, value in config['channels'].items():
                self.channel_widgets[key].channel_label = value['channel_label']
                self.channel_widgets[key].label_box.setPlaceholderText(value['channel_label'])
                
                self.channel_widgets[key].entry_box.setValue(value['channel_value'])
                self.set_value(key)


class ChannelWidget(QWidget):
    def __init__(self,channel_name):
        super().__init__()
        
        self.title = QLabel(channel_name)
        font = self.title.font()
        font.setPointSize(15)
        self.title.setFont(font)
        
        self.channel_label = channel_name
        self.label_box = QLineEdit()
        self.label_box.setPlaceholderText(self.channel_label)
        self.label_box.returnPressed.connect(self.update_channel_label)
        
        self.entry_box = CustomSpinBox()
        self.entry_box.setSuffix("dB")
        self.entry_box.setDisabled(True)
        self.entry_box.setMinimum(0)
        self.entry_box.setMaximum(121)
        
        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.label_box)
        layout.addWidget(self.entry_box)
        
        self.setLayout(layout)
    
    
    def update_channel_label(self):
        self.channel_label = self.label_box.text()
        self.label_box.setPlaceholderText(self.channel_label)
        self.label_box.clear()


class CustomSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.handle_value_change()
        else:
            super().keyPressEvent(event)

    def handle_value_change(self):
        # Emit valueChanged signal for Enter key press
        self.valueChanged.emit(self.value())


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()


