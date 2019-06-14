from datetime import datetime
from functools import partial
from pathlib import Path

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from natsort import natsorted, ns


class Palette:

    @classmethod
    def color(cls, index):
        colors = {
            0: (255, 255, 255),
            1: (38, 190, 33),
            2: (239, 56, 176),
            3: (0, 255, 255),
            4: (255, 255, 0)
        }
        return colors.get(index, (0, 0, 0))


class WarningFrame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setFixedHeight(90)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 5, 30, 5)
        icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(50, 50))
        icon_label.setFixedSize(75, 52)
        layout.addWidget(icon_label)
        text = ("Names of imported images must match\n"
            "in all layers. If an image exists in the \n'image' layer but "
            "not the others, an\nempty image is created automatically.")
        layout.addWidget(QLabel(text))


class FileListDialog(QDialog):

    def __init__(self, layer_name, parent=None, *, files=None):
        super().__init__(parent)
        self._home = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        self.files = files or []
        self.layer_name = layer_name
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedSize(400, 500)
        self.setWindowTitle(f"Layer '{self.layer_name.title()}' - Import")
        self.list_widget = QListWidget(self)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        open_btn = QToolButton()
        open_btn.setIcon(QIcon("icons/open-folder.png"))
        open_btn.clicked.connect(self._pick_files)
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Files to import:"))
        top_bar.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))
        top_bar.addWidget(open_btn)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.addLayout(top_bar)
        layout.addWidget(self.list_widget)
        layout.addWidget(button_box)

        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setTextElideMode(Qt.ElideLeft)

        self.list_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.remove_action = QAction("Remove selected")
        self.clear_action = QAction("Clear selection")
        self.remove_action.triggered.connect(self._remove_selected)
        self.clear_action.triggered.connect(self._clear_selection)
        self.list_widget.addAction(self.remove_action)
        self.list_widget.addAction(self.clear_action)

        if self.files:
            for path in natsorted(self.files, alg=ns.PATH):
                item = QListWidgetItem()
                item.setText(Path(path).name)
                item.setToolTip(Path(path).name)
                item.setSizeHint(QSize(item.sizeHint().width(), 18))
                self.list_widget.addItem(item)

    def _pick_files(self):
        file_paths = QFileDialog.getOpenFileNames(
            self, "Import Images", self._home, "Images (*.png *.jpg *.jpeg *.bmp)")
        if not file_paths[0]:
            return
        for path in file_paths[0]:
            if path in self.files:
                continue
            self.files.append(path)
        self.files = natsorted(self.files, alg=ns.PATH)
        self.list_widget.clear()
        for path in self.files:
            item = QListWidgetItem()
            item.setText(Path(path).name)
            item.setToolTip(Path(path).name)
            item.setSizeHint(QSize(item.sizeHint().width(), 18))
            self.list_widget.addItem(item)

    def _remove_selected(self):
        rows = [self.list_widget.row(i) for i in self.list_widget.selectedItems()]
        for row in reversed(rows):
            item = self.list_widget.takeItem(row)
            if 0 <= row < len(self.files):
                del self.files[row]
            del item
        self._clear_selection()

    def _clear_selection(self):
        self.list_widget.selectionModel().clearSelection()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self._remove_selected()
            return
        super().keyPressEvent(event)


class ProjectDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._home = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        self._docs = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)[0]
        self._color_idx = 0
        self._setup_ui()

        self.masks = []
        self.colors = []
        self.files = []

        self._edit_row(self._new_row(), "image", False, Palette.color(0), interactable=False)
        self._edit_row(self._new_row(), "mask", True, Palette.color(1))

    @property
    def project_path(self):
        return self.edit_project.text()

    @property
    def layers(self):
        names = []
        for i in range(self.table.rowCount()):
            folder = self.table.item(i, 0).text()
            names.append(folder)
        return names

    def _remove_selected(self):
        rows = reversed([i.row() for i in self.table.selectedItems()])
        for row in rows:
            self.table.removeRow(row)
            if 0 <= row < len(self.colors):
                del self.colors[row]
            if 0 <= row < len(self.masks):
                del self.masks[row]
            if 0 <= row < len(self.files):
                del self.files[row]
        self._clear_selection()

    def _clear_selection(self):
        self.table.selectionModel().clearSelection()

    def _validate(self):
        if Path(self.edit_project.text()).exists():
            text = "The selected project file already exists, overwrite?"
            choice = QMessageBox.warning(self, "Project file exists", text,
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if choice == QMessageBox.Cancel:
                return
        for layer_name in self.layers:
            if layer_name.strip() == "":
                text = "Empty layer names are not permitted!"
                QMessageBox.warning(self, "Empty layer name", text, QMessageBox.Ok)
                return
        if len(self.files) > 1:
            image_names = [Path(f).name for f in self.files[0]]
            for mask_list in self.files[1:]:
                for f in mask_list:
                    if Path(f).name in image_names:
                        continue
                    text = f"There is no corresponding image for mask '{Path(f).name}'!"
                    QMessageBox.warning(self, "Missing image!", text, QMessageBox.Ok)
                    return
        if len(self.files[0]) == 0:
            text = "You must import at least one image for the 'image' layer!"
            QMessageBox.warning(self, "No base image imported!", text, QMessageBox.Ok)
            return
        self.accept()

    def _new_row(self):
        row_idx = self.table.rowCount()
        self.table.setRowCount(row_idx + 1)
        self.masks.append(False)
        color = Palette.color(self._color_idx)
        self.colors.append(color)
        self._edit_row(row_idx, f"mask ({self._color_idx})", True, color)
        self._color_idx += 1
        self.files.append([])
        return row_idx

    def _edit_row(self, row, layer_name, is_mask, color, *, interactable=True):
        if not interactable:
            text_item = QTableWidgetItem(layer_name)
            text_item.setFlags(text_item.flags() ^ Qt.ItemIsEnabled)
            self.table.setItem(row, 0, text_item)
            self.table.setCellWidget(row, 1,
                self._mask_checkbox(row, is_mask, enabled=False))
            self.table.setCellWidget(row, 2, self._color_field(row, color, pickable=False))
            self.table.setCellWidget(row, 3, self._import_button(row))
            return

        self.table.setItem(row, 0, QTableWidgetItem(layer_name))
        self.table.setCellWidget(row, 1, self._mask_checkbox(row, is_mask))
        self.table.setCellWidget(row, 2, self._color_field(row, color))
        self.table.setCellWidget(row, 3, self._import_button(row))

    def _find_row(self, widget):
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if self.table.cellWidget(i, j) == widget:
                    return i
        return None

    def _mask_checkbox(self, row, default_value, *, enabled=True):
        widget = QWidget()
        widget.setObjectName("projectDialogRow")
        layout = QHBoxLayout(widget)
        layout.setMargin(0)
        checkbox = QCheckBox()
        checkbox.setChecked(default_value)
        checkbox.setEnabled(enabled)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        checkbox.stateChanged.connect(partial(self._set_mask, widget))
        self.masks[row] = default_value
        return widget

    def _color_field(self, row, color, *, pickable=True):
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
        if pickable:
            button.clicked.connect(
                partial(self._show_color_picker, widget, button))
        self.colors[row] = color
        return widget

    def _import_button(self, row_idx):
        widget = QWidget()
        widget.setObjectName("projectDialogRow")
        move_layout = QHBoxLayout(widget)
        move_layout.setSpacing(0)
        move_layout.setMargin(0)
        move_layout.setAlignment(Qt.AlignCenter)
        import_button = QToolButton()
        import_button.setMaximumSize(12, 12)
        import_button.setObjectName("projectDialogImportImages")
        import_button.clicked.connect(partial(self._show_file_list, row_idx))
        import_button.setIcon(QIcon("icons/add.png"))
        move_layout.addWidget(import_button)
        return widget

    def _show_color_picker(self, widget, button):
        row = self._find_row(widget)
        color = QColorDialog.getColor(QColor(*self.colors[row]))
        if color.isValid():
            self.colors[row] = (color.red(), color.green(), color.blue())
            color_txt = f"{color.red()}, {color.green()}, {color.blue()}"
            button.setStyleSheet(f"background-color: rgb({color_txt});")

    def _set_mask(self, widget, checkbox_state):
        row = self._find_row(widget)
        self.masks[row] = checkbox_state == Qt.Checked

    def _show_file_dialog(self, line_widget):
        filename = QFileDialog.getSaveFileName(
            self, "New Project File", self._home, "Segmate Project File (*.spf)",
            options=QFileDialog.DontConfirmOverwrite)
        if filename[0]:
            if filename[0].endswith(".spf"):
                line_widget.setText(filename[0])
            else:
                line_widget.setText(f"{filename[0]}.spf")

    def _show_file_list(self, row_idx):
        layer_name = self.table.item(row_idx, 0).text()
        dialog = FileListDialog(layer_name, self, files=self.files[row_idx])
        dialog.exec()
        self.files[row_idx] = dialog.files

    def _get_default_path(self):
        num = 1
        date = f"{datetime.now():%Y-%m-%d}"
        path = f"{self._docs}/project-{date}.spf"
        while Path(path).exists():
            path = f"{self._docs}/project-{date}-{num}.spf"
            num += 1
        return path

    def _setup_ui(self):
        self.setFixedSize(420, 450)
        self.setWindowTitle("New Project - Import Files")

        top_box = QVBoxLayout()
        top_box.setSpacing(3)

        project_label = QLabel("Save new project as:")
        project_label.setStyleSheet("border: 0px;")
        layer_label = QLabel("Click '+' to import images:")
        layer_label.setStyleSheet("border: 0px;")

        completer = QCompleter(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        fs_model = QFileSystemModel(completer)
        fs_model.setRootPath(self._docs)
        completer.setModel(fs_model)

        self.edit_project = QLineEdit()
        self.edit_project.setText(self._get_default_path())
        self.edit_project.setCompleter(completer)
        project_button = QToolButton()
        project_button.clicked.connect(partial(self._show_file_dialog, self.edit_project))
        project_button.setIcon(QIcon("icons/open-folder.png"))
        project_layout = QHBoxLayout()
        project_layout.addWidget(self.edit_project)
        project_layout.addWidget(project_button)

        top_box.addWidget(project_label)
        top_box.addLayout(project_layout)

        self.table = QTableWidget(self)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)

        self.table.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.remove_action = QAction("Remove selected")
        self.clear_action = QAction("Clear selection")
        self.remove_action.triggered.connect(self._remove_selected)
        self.clear_action.triggered.connect(self._clear_selection)
        self.table.addAction(self.remove_action)
        self.table.addAction(self.clear_action)

        self.table.setColumnCount(4)
        self.table.verticalHeader().setVisible(False)

        self.table.setHorizontalHeaderItem(0, QTableWidgetItem("Layer"))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem("Mask"))
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem("Color"))
        self.table.setHorizontalHeaderItem(3, QTableWidgetItem("    "))

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addLayout(top_box)
        layout.addWidget(WarningFrame())

        table_layout = QVBoxLayout()
        table_layout.setSpacing(3)
        table_layout.addWidget(layer_label)
        table_layout.addWidget(self.table)

        layout.addLayout(table_layout)
        new_row_btn = QToolButton()
        new_row_btn.setObjectName("dialogAddRow")
        new_row_btn.setText(" Add Layer")
        new_row_btn.setIcon(QIcon("icons/add.png"))
        new_row_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        new_row_btn.clicked.connect(self._new_row)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._validate)
        button_box.rejected.connect(self.reject)
        layout.addWidget(new_row_btn)
        layout.addWidget(button_box)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            return
        if event.key() == Qt.Key_Delete:
            self._remove_selected()
            return
        super().keyPressEvent(event)
