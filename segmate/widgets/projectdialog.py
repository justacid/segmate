from datetime import datetime
from os import listdir
from os.path import isdir, isfile
from functools import partial

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class ProjectDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(420, 450)
        self.setWindowTitle("New Project - Import Files")
        self._home = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]

        self.masks = []
        self.editable = []
        self.colors = []

        self._palette = {
            0: (255, 255, 255),
            1: (38, 190, 33),
            2: (239, 56, 176),
            3: (0, 255, 255),
            4: (255, 255, 0)
        }

        top_box = QVBoxLayout()
        top_box.setSpacing(3)

        folder_label = QLabel("Select data folder:")
        folder_label.setStyleSheet("border: 0px;")
        project_label = QLabel("Save as:")
        project_label.setStyleSheet("border: 0px;")

        completer = QCompleter(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        fs_model = QFileSystemModel(completer)
        fs_model.setRootPath(self._home)
        completer.setModel(fs_model)

        self.edit_folder = QLineEdit()
        self.edit_folder.setText(self._home)
        self.edit_folder.returnPressed.connect(
            partial(self._folder_edited, self.edit_folder))
        self.edit_folder.setCompleter(completer)

        folder_button = QToolButton()
        folder_button.clicked.connect(partial(self._show_folder_dialog, self.edit_folder))
        folder_button.setIcon(QIcon("icons/open-folder.png"))
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.edit_folder)
        folder_layout.addWidget(folder_button)

        self.edit_project = QLineEdit()
        date = f"{datetime.now():%Y-%m-%d}"
        self.edit_project.setText(f"{self._home}/segmate-project-{date}.spf")
        self.edit_project.setCompleter(completer)
        project_button = QToolButton()
        project_button.clicked.connect(partial(self._show_file_dialog, self.edit_project))
        project_button.setIcon(QIcon("icons/open-folder.png"))
        project_layout = QHBoxLayout()
        project_layout.addWidget(self.edit_project)
        project_layout.addWidget(project_button)

        top_box.addWidget(folder_label)
        top_box.addLayout(folder_layout)
        top_box.addWidget(project_label)
        top_box.addLayout(project_layout)

        self.table = QTableWidget(self)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.table.setTabKeyNavigation(False)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)

        self.table.setColumnCount(5)
        self.table.verticalHeader().setVisible(False)

        self.table.setHorizontalHeaderItem(0, QTableWidgetItem("Folder"))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem("Mask"))
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem("Editable"))
        self.table.setHorizontalHeaderItem(3, QTableWidgetItem("Color"))
        self.table.setHorizontalHeaderItem(4, QTableWidgetItem("(Re)Move"))

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addLayout(top_box)
        layout.addWidget(self.table)
        new_row_btn = QToolButton()
        new_row_btn.setObjectName("dialogAddRow")
        new_row_btn.clicked.connect(self._add_row)
        new_row_btn.setIcon(QIcon("icons/add.png"))
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._validate_input)
        button_box.rejected.connect(self.reject)
        layout.addWidget(new_row_btn)
        layout.addWidget(button_box)

    @property
    def project_path(self):
        return self.edit_project.text()

    @property
    def data_root(self):
        return self.edit_folder.text()

    @property
    def folders(self):
        names = []
        for i in range(self.table.rowCount()):
            folder = self.table.item(i, 0).text()
            names.append(folder)
        return names

    def _validate_input(self):
        if isfile(self.edit_project.text()):
            text = "The selected project file already exists, overwrite?"
            retval = self._show_error_message("File Exists!", text, yesno=True)
            if retval == QMessageBox.No:
                return

        folders = self.folders
        if not folders:
            self.reject()
            return
        for folder in folders:
            if folder.strip() == "":
                text = "All folder names must be set in order to proceed."
                self._show_error_message("Error!", text)
                return
        self.accept()

    def _show_error_message(self, title, text, yesno=False):
        msgbox = QMessageBox(self)
        msgbox.setWindowTitle(title)
        msgbox.setText(text)
        if yesno:
            msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgbox.setDefaultButton(QMessageBox.No)
            msgbox.setIcon(QMessageBox.Warning)
        else:
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.setDefaultButton(QMessageBox.Ok)
            msgbox.setIcon(QMessageBox.Critical)
        return msgbox.exec()

    def _add_row(self):
        row = self.table.rowCount()
        self.table.setRowCount(row + 1)
        self.masks.append(False)
        self.editable.append(False)
        color = self._palette.get(row, (0, 0, 0))
        self.colors.append(color)
        self._set_row(row, "", False, False, color)
        return row

    def _set_row(self, row, folder, is_mask, is_editable, color):
        self.table.setItem(row, 0, QTableWidgetItem(folder))
        self.table.setCellWidget(row, 1, self._mask_widget(row, is_mask))
        self.table.setCellWidget(row, 2, self._editable_widget(row, is_editable))
        self.table.setCellWidget(row, 3, self._color_widget(row, color))
        self.table.setCellWidget(row, 4, self._move_row_widget())

    def _delete_row(self, widget):
        row = self._find_row(widget)
        del self.masks[row]
        del self.editable[row]
        del self.colors[row]
        self.table.removeRow(row)

    def _find_row(self, widget):
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if self.table.cellWidget(i, j) == widget:
                    return i
        return None

    def _move_row_up(self, widget):
        row = self._find_row(widget)
        if row <= 0:
            return

        text = self.table.item(row, 0).text()
        mask = self.masks[row]
        editable = self.editable[row]
        color = self.colors[row]

        text2 = self.table.item(row-1, 0).text()
        mask2 = self.masks[row-1]
        editable2 = self.editable[row-1]
        color2 = self.colors[row-1]

        self._set_row(row, text2, mask2, editable2, color2)
        self._set_row(row-1, text, mask, editable, color)

    def _move_row_down(self, widget):
        row = self._find_row(widget)
        if row >= self.table.rowCount()-1:
            return

        text = self.table.item(row, 0).text()
        mask = self.masks[row]
        editable = self.editable[row]
        color = self.colors[row]

        text2 = self.table.item(row+1, 0).text()
        mask2 = self.masks[row+1]
        editable2 = self.editable[row+1]
        color2 = self.colors[row+1]

        self._set_row(row, text2, mask2, editable2, color2)
        self._set_row(row+1, text, mask, editable, color)

    def _mask_widget(self, row, default_value):
        widget = QWidget()
        widget.setObjectName("projectDialogRow")
        layout = QHBoxLayout(widget)
        layout.setMargin(0)
        checkbox = QCheckBox()
        checkbox.setChecked(default_value)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        checkbox.stateChanged.connect(partial(self._set_mask, widget))
        self.masks[row] = default_value
        return widget

    def _editable_widget(self, row, default_value):
        widget = QWidget()
        widget.setObjectName("projectDialogRow")
        layout = QHBoxLayout(widget)
        layout.setMargin(0)
        checkbox = QCheckBox()
        checkbox.setChecked(default_value)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        checkbox.stateChanged.connect(partial(self._set_editable, widget))
        self.editable[row] = default_value
        return widget

    def _color_widget(self, row, color):
        widget = QWidget()
        widget.setObjectName("projectDialogRow")
        layout = QHBoxLayout(widget)
        layout.setMargin(0)
        button = QPushButton()
        color_txt = ','.join([str(c) for c in color])
        button.setObjectName("colorSelector")
        button.setStyleSheet(f"background-color: rgb({color_txt});")
        layout.addWidget(button)
        layout.setAlignment(Qt.AlignCenter)
        button.clicked.connect(
            partial(self._show_color_picker, widget, button))
        self.colors[row] = color
        return widget

    def _move_row_widget(self):
        widget = QWidget()
        widget.setObjectName("projectDialogRow")
        move_layout = QHBoxLayout(widget)
        move_layout.setSpacing(0)
        move_layout.setMargin(0)
        move_layout.setAlignment(Qt.AlignCenter)
        up_button = QToolButton()
        up_button.setMaximumSize(18, 18)
        up_button.setArrowType(Qt.UpArrow)
        up_button.clicked.connect(partial(self._move_row_up, widget))
        down_button = QToolButton()
        down_button.setMaximumSize(18, 18)
        down_button.setArrowType(Qt.DownArrow)
        down_button.clicked.connect(partial(self._move_row_down, widget))
        delete_button = QToolButton()
        delete_button.setMaximumSize(10, 10)
        delete_button.setObjectName("projectDialogDeleteRow")
        delete_button.clicked.connect(partial(self._delete_row, widget))
        delete_button.setIcon(QIcon("icons/remove.png"))
        move_layout.addWidget(up_button)
        move_layout.addWidget(down_button)
        move_layout.addSpacerItem(QSpacerItem(5, 5, QSizePolicy.Fixed, QSizePolicy.Fixed))
        move_layout.addWidget(delete_button)
        return widget

    def _show_color_picker(self, widget, button):
        row = self._find_row(widget)
        color = QColorDialog.getColor(QColor(*self.colors[row]))
        if color.isValid():
            self.colors[row] = (color.red(), color.green(), color.blue())
            color_txt = f"{color.red()}, {color.green()}, {color.blue()}"
            button.setStyleSheet(f"background-color: rgb({color_txt});")

    def _set_editable(self, widget, checkbox_state):
        row = self._find_row(widget)
        self.editable[row] = checkbox_state == Qt.Checked

    def _set_mask(self, widget, checkbox_state):
        row = self._find_row(widget)
        self.masks[row] = checkbox_state == Qt.Checked

    def _show_folder_dialog(self, line_widget):
        init_dir = self._home
        if isdir(line_widget.text()):
            init_dir = line_widget.text()

        folder = QFileDialog.getExistingDirectory(self, "Open Directory...", init_dir)
        if folder:
            line_widget.setText(folder)
            self._populate_table(folder)

    def _show_file_dialog(self, line_widget):
        filename = QFileDialog.getSaveFileName(
            self, "New Project File", self._home, "Segmate Project File (*.spf)",
            options=QFileDialog.DontConfirmOverwrite)
        if filename[0]:
            if filename[0].endswith(".spf"):
                line_widget.setText(filename[0])
            else:
                line_widget.setText(f"{filename[0]}.spf")

    def _folder_edited(self, line_widget):
        folder = line_widget.text()
        if isdir(folder):
            self._populate_table(folder)
        else:
            self.table.setRowCount(0)

    def _populate_table(self, folder):
        subfolders = [f for f in listdir(folder) if isdir(f"{folder}/{f}")]

        self.table.setRowCount(0)
        self.masks.clear()
        self.editable.clear()
        self.colors.clear()

        for subfolder in subfolders:
            row = self._add_row()
            first = True if row != 0 else False
            color = self._palette.get(row, (0, 0, 0))
            self._set_row(row, subfolder, first, first, color)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            return
        super().keyPressEvent(event)
