import json
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QLineEdit, QMessageBox, QHBoxLayout, QFileDialog, QScrollArea, QCheckBox, QSpinBox, QDialog
)
import time
from PyQt5.QtGui import QIcon

SAVE_FILE = "saved_data.json"


def load_saved_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}

def save_data(data):
    with open(SAVE_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def extract_token_and_nickname(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        current_account = data.get("currentAccount")
        token = data.get("accounts", {}).get(current_account, "")

        if current_account:
            return current_account, token, data
        else:
            return None, None, None
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        return None, None, None
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON: {e}")
        return None, None, None

def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        settings = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                settings[key.strip()] = value.strip()
        return settings
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Ошибка чтения options.txt файла: {e}")
        return {}

def write_txt_file(file_path, settings):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for key, value in settings.items():
                file.write(f"{key}:{value}\n")
    except Exception as e:
        print(f"Ошибка записи options.txt файла: {e}")


class CristalixAccountChanger(QMainWindow):
    def __init__(self):
        super().__init__()

        self.saved_data = load_saved_data()



        self.setWindowTitle("CristalixAccountChanger")
        self.setGeometry(100, 100, 600, 600)
        self.setFixedSize(600, 600)
        self.setWindowIcon(QIcon('dev.ico'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Инициализация полей для путей
        self.entry_file_path = QLineEdit()
        self.entry_program_path = QLineEdit()
        self.entry_txt_path = QLineEdit()

        # Кнопка для открытия окна настроек
        self.button_open_settings = QPushButton("Открыть настройки")
        self.button_open_settings.clicked.connect(self.open_settings_window)
        self.layout.addWidget(self.button_open_settings)

        # Настройки памяти, чанков и ФПС
        self.label_memory_amount = QLabel("Укажите количество памяти (MB):")
        self.layout.addWidget(self.label_memory_amount)

        self.memory_amount_spinner = QSpinBox()
        self.memory_amount_spinner.setMinimum(1024)  # Минимум 1024 MB
        self.memory_amount_spinner.setMaximum(8192)  # Максимум 8 GB
        self.layout.addWidget(self.memory_amount_spinner)

        self.label_render_distance = QLabel("Укажите чанки:")
        self.layout.addWidget(self.label_render_distance)

        self.render_distance_spinner = QSpinBox()
        self.render_distance_spinner.setMinimum(0)  # Минимум 0
        self.render_distance_spinner.setMaximum(32)  # Максимум 32
        self.layout.addWidget(self.render_distance_spinner)

        self.label_max_fps = QLabel("Укажите ФПС:")
        self.layout.addWidget(self.label_max_fps)

        self.max_fps_spinner = QSpinBox()
        self.max_fps_spinner.setMinimum(1)  # Минимум 0
        self.max_fps_spinner.setMaximum(255)  # Максимум 255
        self.layout.addWidget(self.max_fps_spinner)

        # Кнопки
        self.button_save_txt_settings = QPushButton("Сохранить настройки в options")
        self.button_save_txt_settings.clicked.connect(self.save_txt_settings)
        self.button_save_memory = QPushButton("Сохранить память")
        self.button_save_memory.clicked.connect(self.save_memory_amount)
        self.button_load = QPushButton("Загрузить аккаунт")
        self.button_load.clicked.connect(self.on_select_file)

        # Создаем горизонтальный лэйаут для первой строки кнопок
        self.button_layout_1 = QHBoxLayout()
        self.button_layout_1.addWidget(self.button_save_txt_settings)
        self.button_layout_1.addWidget(self.button_save_memory)
        self.button_layout_1.addWidget(self.button_load)

        self.layout.addLayout(self.button_layout_1)

        self.button_run_selected = QPushButton("Запустить выбранные аккаунты")
        self.button_run_selected.clicked.connect(self.run_selected_accounts)
        self.button_run_all = QPushButton("Запустить все аккаунты")
        self.button_run_all.clicked.connect(self.run_all_accounts)

        # Создаем горизонтальный лэйаут для второй строки кнопок
        self.button_layout_2 = QHBoxLayout()
        self.button_layout_2.addWidget(self.button_run_selected)
        self.button_layout_2.addWidget(self.button_run_all)

        self.layout.addLayout(self.button_layout_2)

        self.label_status = QLabel("")
        self.layout.addWidget(self.label_status)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout.addWidget(self.scroll_area)

        # Добавляем плашку с автором
        self.footer_layout = QHBoxLayout()
        self.footer_label = QLabel("Coded by: iJuspBentley")
        self.footer_label.setStyleSheet("color: gray; font-size: 12px; font-weight: bold;")
        self.footer_layout.addStretch()
        self.footer_layout.addWidget(self.footer_label)
        self.layout.addLayout(self.footer_layout)

        self.update_list()

    def open_settings_window(self):
        settings_window = QDialog(self)  # Используем QDialog вместо QWidget
        settings_window.setWindowTitle("Настройки")
        settings_window.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout(settings_window)

        # Путь к .launcher
        self.label_file_path = QLabel("Введите путь к файлу .launcher:")
        layout.addWidget(self.label_file_path)

        self.file_path_layout = QHBoxLayout()
        self.file_path_layout.addWidget(self.entry_file_path)

        self.button_browse = QPushButton("Обзор")
        self.button_browse.clicked.connect(self.browse_file)
        self.file_path_layout.addWidget(self.button_browse)

        layout.addLayout(self.file_path_layout)

        # Путь к Cristalix
        self.label_program_path = QLabel("Введите путь к Cristalix:")
        layout.addWidget(self.label_program_path)

        self.program_path_layout = QHBoxLayout()
        self.program_path_layout.addWidget(self.entry_program_path)

        self.button_browse_program = QPushButton("Обзор")
        self.button_browse_program.clicked.connect(self.browse_program)
        self.program_path_layout.addWidget(self.button_browse_program)

        layout.addLayout(self.program_path_layout)

        # Путь к options.txt
        self.label_txt_path = QLabel("Введите путь к options.txt (опционально):")
        layout.addWidget(self.label_txt_path)

        self.txt_path_layout = QHBoxLayout()
        self.txt_path_layout.addWidget(self.entry_txt_path)

        self.button_browse_txt = QPushButton("Обзор")
        self.button_browse_txt.clicked.connect(self.browse_txt_file)
        self.txt_path_layout.addWidget(self.button_browse_txt)

        layout.addLayout(self.txt_path_layout)

        # Кнопка для закрытия окна настроек
        button_close = QPushButton("Закрыть")
        button_close.clicked.connect(settings_window.close)
        layout.addWidget(button_close)

        settings_window.setLayout(layout)
        settings_window.exec_()



    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Выберите JSON файл", "", "JSON Files (*.launcher);;All Files (*)")
        if file_path:
            self.entry_file_path.setText(file_path)
            self.saved_data['last_file_path'] = file_path
            save_data(self.saved_data)

    def browse_program(self):
        file_dialog = QFileDialog()
        program_path, _ = file_dialog.getOpenFileName(self, "Выберите программу", "",
                                                      "Executables (*.exe);;All Files (*)")
        if program_path:
            self.entry_program_path.setText(program_path)
            self.saved_data['last_program_path'] = program_path
            save_data(self.saved_data)

    def browse_txt_file(self):
        file_dialog = QFileDialog()
        txt_path, _ = file_dialog.getOpenFileName(self, "Выберите TXT файл", "", "Text Files (*.txt);;All Files (*)")
        if txt_path:
            self.entry_txt_path.setText(txt_path)
            self.saved_data['last_txt_path'] = txt_path
            save_data(self.saved_data)

    def save_txt_settings(self):
        txt_path = self.entry_txt_path.text()
        if not txt_path:
            QMessageBox.warning(self, "Ошибка", "Введите путь к .txt файлу.")
            return

        try:
            settings = read_txt_file(txt_path)

            # Обновляем настройки
            settings["maxFps"] = str(self.max_fps_spinner.value())
            settings["renderDistance"] = str(self.render_distance_spinner.value())

            write_txt_file(txt_path, settings)
            QMessageBox.information(self, "Успех", "Настройки успешно сохранены в options.txt файл.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить настройки: {e}")

    def save_txt_path(self):
        txt_path = self.entry_txt_path.text()
        if txt_path:
            self.saved_data['last_txt_path'] = txt_path
            save_data(self.saved_data)


    def on_select_file(self):
        file_path = self.entry_file_path.text()
        if not file_path:
            self.label_status.setText("Введите путь к файлу.")
            return

        nickname, token, _ = extract_token_and_nickname(file_path)
        if nickname and token:
            self.saved_data[nickname] = token
            save_data(self.saved_data)
            self.update_list()
            self.label_status.setText("Данные успешно загружены.")
        else:
            self.label_status.setText("Не удалось найти никнейм или токен.")

    def save_memory_amount(self):
        file_path = self.entry_file_path.text()
        if not file_path:
            QMessageBox.warning(self, "Ошибка", "Введите путь к .launcher файлу.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            memory_amount = self.memory_amount_spinner.value()
            data["memoryAmount"] = memory_amount

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "Успех", "Память успешно обновлена.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить изменения: {e}")

    def update_list(self):
        print("Обновление списка аккаунтов...")


        # Очищаем список
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        # Отображаем только данные аккаунтов
        for nickname, token in self.saved_data.items():
            if nickname in ['last_file_path', 'last_program_path', 'last_txt_path']:
                continue
            print(f"Добавление аккаунта: {nickname}")

            item_widget = QWidget()
            item_layout = QHBoxLayout()
            item_widget.setLayout(item_layout)

            checkbox = QCheckBox(nickname)
            item_layout.addWidget(checkbox)

            # Скрываем часть токена
            hidden_token = f"{token[:5]}..." if token else "Токен отсутствует"
            label = QLabel(hidden_token)
            item_layout.addWidget(label)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda _, nick=nickname: self.delete_account(nick))
            item_layout.addWidget(delete_button)

            self.scroll_layout.addWidget(item_widget)

            # Сохраняем чекбокс в атрибуты для доступа
            checkbox.nickname = nickname
            checkbox.token = token

    def delete_account(self, nickname):
        if nickname in self.saved_data:
            del self.saved_data[nickname]
            save_data(self.saved_data)
            self.update_list()
            QMessageBox.information(self, "Успех", f"Аккаунт {nickname} успешно удалён.")
        else:
            QMessageBox.warning(self, "Ошибка", f"Аккаунт {nickname} не найден.")

    def get_selected_accounts(self):
        selected_accounts = []
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            checkbox = widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                selected_accounts.append((checkbox.nickname, checkbox.token))
        return selected_accounts

    def run_selected_accounts(self):
        selected_accounts = self.get_selected_accounts()
        if not selected_accounts:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один аккаунт.")
            return
        self.run_accounts(selected_accounts)

    def run_all_accounts(self):
        accounts = [
            (nickname, token) for nickname, token in self.saved_data.items()
            if nickname not in ['last_file_path', 'last_program_path', 'last_txt_path']
        ]
        if not accounts:
            QMessageBox.warning(self, "Ошибка", "Нет доступных аккаунтов для запуска.")
            return
        self.run_accounts(accounts)

    def run_accounts(self, accounts):
        file_path = self.entry_file_path.text()
        program_path = self.entry_program_path.text()

        if not file_path or not program_path:
            QMessageBox.warning(self, "Ошибка", "Убедитесь, что указаны пути к .launcher и Cristalix.")
            return

        for nickname, token in accounts:
            _, _, original_data = extract_token_and_nickname(file_path)

            if not original_data:
                QMessageBox.warning(self, "Ошибка", f"Не удалось прочитать .launcher для аккаунта {nickname}.")
                continue

            # Изменяем файл
            original_data["currentAccount"] = nickname
            if "accounts" in original_data:
                original_data["accounts"][nickname] = token

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(original_data, file, ensure_ascii=False, indent=4)

            # Запускаем кристу
            try:
                subprocess.Popen([program_path], shell=True)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось запустить Cristalix для аккаунта {nickname}: {e}")
                continue

            # Кд между запусками кристаликсов, меньше 5 секунд не рекомендую.
            time.sleep(5)

        QMessageBox.information(self, "Готово", "Запуск аккаунтов завершён.")

if __name__ == "__main__":
    app = QApplication([])
    window = CristalixAccountChanger()
    if 'last_file_path' in window.saved_data:
        window.entry_file_path.setText(window.saved_data['last_file_path'])
    if 'last_program_path' in window.saved_data:
        window.entry_program_path.setText(window.saved_data['last_program_path'])
    if 'last_txt_path' in window.saved_data:
        window.entry_txt_path.setText(window.saved_data['last_txt_path'])
    window.show()
    app.exec()