from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget, QSizePolicy


class CollapsibleFrame(QFrame):
    widget_list = []

    def __init__(self, label, *args, color="blue", parent=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName(f"myFrame_{color}")
        self.setStyleSheet(
            f"#myFrame_{color}"
            + " { padding: 15px 15px 15px 15px; border: 2px solid "
            + color
            + "}"
        )
        self.adjustSize()
        self.setContentsMargins(6, 14, 6, 6)

        self.layout = QHBoxLayout()
        self.widget = QWidget()
        self.layout.addWidget(self.widget)

        CollapsibleFrame.widget_list += [self]
        label_frame = QLabel(self)
        label_frame.setObjectName(f"myLabel_{color}")
        label_frame.setStyleSheet(f"padding: 40px 10px; color:{color}")
        label_frame.setMinimumWidth(500)
        # label_frame.adjustSize()
        label_frame.mousePressEvent = self.label_clicked
        self.label = label_frame
        self.label_txt = label
        self.label.setText("▼  " + self.label_txt)
        super().setLayout(self.layout)

    def setLayout(self, *args, **kwargs):
        self.widget.setLayout(*args, **kwargs)

    def setCollapsed(self, is_collasped=True):
        if not is_collasped:
            self.widget.setVisible(True)
            self.label.setText("▼  " + self.label_txt)
            self.setFixedHeight(self.layout.sizeHint().height() + 15)

        else:
            self.widget.setVisible(False)
            self.label.setText("▶  " + self.label_txt)
            self.setFixedHeight(self.layout.sizeHint().height() + 15)

        self.adjustSize()
        self.setContentsMargins(6, 14, 6, 1)

    def label_clicked(self, event):
        if self.widget.isVisible():
            self.setCollapsed(True)
        else:
            self.setCollapsed(False)

    @classmethod
    def collapse_all(cls):
        for wdg in cls.widget_list:
            wdg.setCollapsed(True)

    @classmethod
    def uncollapse_all(cls):
        for wdg in cls.widget_list:
            wdg.setCollapsed(False)


if __name__ == "__main__":

    import sys
    from random import randint
    from PyQt5.QtWidgets import QLabel, QDialog, QApplication, QHBoxLayout, QVBoxLayout, QPushButton

    class MainWindow(QDialog):
        def __init__(self):
            super().__init__()

            layout = QVBoxLayout()
            for i, color in enumerate(['blue', 'red', 'yellow', 'green', 'brown']):
                wdg = CollapsibleFrame(f'Frame {i}', color=color)
                wdg_layout = QHBoxLayout()
                label = QLabel('Put any widget you want')
                wdg_layout.addWidget(label)
                wdg.setLayout(wdg_layout)
                wdg.setCollapsed(randint(0,1))
                layout.addWidget(wdg)

            btn_collapse_all = QPushButton("collapse all")
            btn_collapse_all.clicked.connect(CollapsibleFrame.collapse_all)
            btn_uncollapse_all = QPushButton("open all")
            btn_uncollapse_all.clicked.connect(CollapsibleFrame.uncollapse_all)

            layout.addWidget(btn_collapse_all)
            layout.addWidget(btn_uncollapse_all)

            self.setLayout(layout)

    app = QApplication(sys.argv)
    window = MainWindow()#*parse_args())
    window.show()
    sys.exit(app.exec_())


