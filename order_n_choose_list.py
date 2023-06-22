from PyQt5.QtCore import Qt, QTimer, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QAbstractItemView


class OrderNChooseWdg(QListView):

    def __init__(self):
        super().__init__()

        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropOverwriteMode(False)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)

        self.old_row = -1000
        self.is_shift_pressed = False
        self.item_list = []

        self.model = QStandardItemModel(self)
        self.model.rowsInserted.connect(self.get_inserted_row)
        self.model.dataChanged.connect(self.get_states)

        self.setModel(self.model)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def keyPressEvent(self, e):

        if e.key() == Qt.Key_Shift:

            self.is_shift_pressed = True

        # Move selected QStandardItem up or down in QListView
        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            row = indexes[0].row()

            if self.is_shift_pressed:

                if e.key() == Qt.Key_Up:

                    if row > 0:
                        item = self.model.takeRow(row)
                        self.model.insertRow(row - 1, item)
                        self.new_row = row - 1
                        QTimer.singleShot(1, self.update_selection)

                elif e.key() == Qt.Key_Down:

                    if row < self.model.rowCount() - 1:
                        item = self.model.takeRow(row)
                        self.model.insertRow(row + 1, item)
                        self.new_row = row + 1
                        QTimer.singleShot(1, self.update_selection)

        QListView.keyPressEvent(self, e)

    def keyReleaseEvent(self, e):

        if e.key() == Qt.Key_Shift:
            self.is_shift_pressed = False

    def get_states(self):

        dicos = {}

        for i in range(self.model.rowCount()):
            name = self.model.item(i).text()
            state = self.model.item(i).checkState()

            dicos[name] = state

        return dicos

    def get_inserted_row(self, parent, row_inserted, row_end):

        self.new_row = row_inserted  # save index to update selection

        if self.old_row < self.new_row:
            self.new_row += -1  # don't count current item, it will be removed

        # Give delay after item changed to get right row value
        QTimer.singleShot(1, self.get_states)
        QTimer.singleShot(1, self.update_selection)

    def mousePressEvent(self, e):
        """Trigger 'set_old_row' with a small delay so new selection is effective"""

        # Save index (after small delay) in case of drag'n'drop
        QTimer.singleShot(1, self.set_old_row)

        QListView.mousePressEvent(self, e)

    def set_old_row(self):
        """Save currently selected item row (on mouse event) before draging it"""

        indexes = self.selectionModel().selectedIndexes()
        if indexes:
            self.old_row = indexes[0].row()

    def update_selection(self):
        """Highlight item that have been moved given its new row"""

        index = self.model.index(self.new_row, 0)
        self.selectionModel().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)
        self.scrollTo(index)

    def add_item(self, name, state):

        item = QStandardItem(name)

        item.setCheckable(True)
        item.setCheckState(state)
        item.setDragEnabled(True)
        item.setDropEnabled(False)
        item.setToolTip("Drag and drop or 'shift + arrows' to change tab order")

        self.model.appendRow(item)
        self.item_list += [{name: item}]


if __name__ == "__main__":

    import sys
    from random import randint
    from PyQt5.QtWidgets import QLabel, QDialog, QApplication, QHBoxLayout, QVBoxLayout, QPushButton

    class MainWindow(QDialog):
        def __init__(self):
            super().__init__()

            layout = QVBoxLayout()
            label = QLabel('Usage:\n\n   - mouse : click on box to set, drag and drop to mode\n   - keyboard : space to set, shift+arrow to move\n')
            listwdg = OrderNChooseWdg()
            for i in range(8):
                listwdg.add_item(f"entry {i}", 2*(randint(0, 1)))

            btn = QPushButton("Get")
            btn.clicked.connect(lambda : print(listwdg.get_states()))
            layout.addWidget(label)
            layout.addWidget(listwdg)
            layout.addWidget(btn)

            self.setLayout(layout)

    app = QApplication(sys.argv)
    window = MainWindow()#*parse_args())
    window.show()
    sys.exit(app.exec_())


