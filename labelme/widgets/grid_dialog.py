from qtpy import QT_VERSION
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

from labelme.logger import logger

QT5 = QT_VERSION[0] == "5"


class GridDialog(QtWidgets.QDialog):
    def __init__(
        self,
        text="Configure Grid",
        parent=None,
        fit_to_content=None,
        flags=None,
        row=2,
        col=2,
        margin=0
    ):
        if fit_to_content is None:
            fit_to_content = {"row": False, "column": True}
        self._fit_to_content = fit_to_content
        super(GridDialog, self).__init__(parent)

        self.row = row
        self.col = col
        self.margin = margin

        layout = QtWidgets.QVBoxLayout()
        self.edit_row = QtWidgets.QLineEdit()
        layout_edit_row = QtWidgets.QHBoxLayout()
        layout_edit_row.addWidget(QtWidgets.QLabel(self.tr("Rows: ")), 1)
        layout_edit_row.addWidget(self.edit_row, 1)
        layout.addLayout(layout_edit_row)

        layout_edit_col = QtWidgets.QHBoxLayout()
        self.edit_col = QtWidgets.QLineEdit()
        layout_edit_col.addWidget(QtWidgets.QLabel(self.tr("Columns: ")), 1)
        layout_edit_col.addWidget(self.edit_col, 1)
        layout.addLayout(layout_edit_col)

        layout_edit_margin = QtWidgets.QHBoxLayout()
        self.edit_margin = QtWidgets.QLineEdit()
        layout_edit_margin.addWidget(QtWidgets.QLabel(self.tr("Margin between cells: ")), 1)
        layout_edit_margin.addWidget(self.edit_margin, 1)
        layout.addLayout(layout_edit_margin)
        
        # buttons
        self.buttonBox = bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self,
        )
        bb.button(bb.Ok)
        bb.button(bb.Cancel)
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)
        self.setLayout(layout)

    def validate(self):
        row = self.edit_row.text().strip()
        col = self.edit_col.text().strip()
        margin = self.edit_margin.text().strip()
        try:
            r, c, m = int(row), int(col), int(margin)
            if r <= 0 or c <= 0 or m < 0:
                raise Exception
            self.row, self.col, self.margin = r, c, m
            self.accept()
        except Exception:
            QtWidgets.QMessageBox.warning(self, "Error",
                                          "Validating configuration failed.\
                                              Try Again.",
                                          QtWidgets.QMessageBox.Ok)
                            
    def popUp(self, text=None, move=True, flags=None, group_id=None):
        logger.info("Grid Configure")
        self.edit_col.setText(f'{self.col}')
        self.edit_row.setText(f'{self.row}')
        self.edit_margin.setText(f'{self.margin}')
        if move:
            self.move(QtGui.QCursor.pos())
        if self.exec_():
            return self.row, self.col, self.margin
        return 0