
import pyqtgraph as pg

class SpeedProgressBar(pg.PlotWidget):
    """A ProgressBar that show both progress and speed:
        - abscissa : progress [unit], with unit, the unit of data given by user
        - ordonnate : speed [unit/time]
    """

    def __init__(self, parent=None, nb_sections=500, smooth_window=1):
        """Initialize the plot : Hide axis, prevent mouse interactions
        initialize values

        Parameters
        ----------
        nb_sections : int
            Number of vertical bar in the graph
        smooth_window : int
            Use average of last speed bars value to smooth datas (prettier?)
        """

        super().__init__(parent, background='w')

        # Number of bar in the graph
        self.nb_sections = nb_sections

        # Hide axis
        self.plotItem.showAxes(False)
        self.plotItem.showGrid(False)

        # Store last speed values to smooth_window the graph
        self.speed = deque([], maxlen=smooth_window)

        # Disable mouse interactions
        self.setMouseEnabled(False)
        self.plotItem.setMenuEnabled(False)
        self.plotItem.setMouseEnabled(False)
        self.wheelEvent = lambda *args, **kwargs: None
        self.mouseDragEvent = lambda *args, **kwargs: None
        self.mousePressEvent = lambda *args, **kwargs: None
        self.mouseReleaseEvent = lambda *args, **kwargs: None

        # Store the graph object
        self.bargraph = None

    def init(self, max_value):
        """Initialise a bar graph at zero for each x

        Parameters
        ----------
        max_value : int, float
            value at which progressbar reach 100%, could be number of items, sum of files size to process...
            Set to 100 to work in percentage
        """

        self.nb_sections = int(min(self.nb_sections, max_value)) # max bar number
        self.bar_width = max_value // self.nb_sections # "width" of bar
        self.bar_index = 0 # count bar index
        self.bar_previous_index = 0 # hold previous bar index

        # remove last bar and clean plot
        del(self.bargraph)
        self.clear()

        # Init bar at 0
        x = range(self.nb_sections + 1)
        y = [0 for _ in x]
        self.bargraph = pg.BarGraphItem(x = x, height = y, width = 1, brush ='c', pen=pg.mkPen(None))
        self.addItem(self.bargraph)

        # start a timer to update the plot
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # 50ms

        # Start to mesure time
        self.tic = None# time.time()

        # Store bargraph values
        self.new_ys = self.bargraph.opts['height']

    def update_plot(self):
        """Update bar graph given new Y values"""

        self.bargraph.setOpts(**{'heigth':self.new_ys})

    def update_bar(self, progress_value):
        """update bar Y values

        Parameters
        ----------
        progress_value : int, float

        """

        # Create a new bar on graph
        bar_index = int(progress_value // self.bar_width)

        # while bar is not complete skip
        if bar_index == self.bar_previous_index:
            return

        # get last elapsed time
        toc = time.time() - self.tic if self.tic else 3600 # first time init
        self.tic = time.time()

        # compute speed
        self.speed.append((self.bar_width) / toc) # speed of bar

        # if new progress_value is larger than bar width
        for index in range(self.bar_previous_index + 1, bar_index + 1):

            # Set speed at bar_index
            ys = self.bargraph.opts['height']
            ys[index] = sum(self.speed) / len(self.speed)
            self.new_ys = ys

        self.bar_previous_index = bar_index


#### END #####


if __name__ == "__main__":

    from random import randint
    from collections import deque
    import sys
    import time

    from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpinBox, QPushButton, QVBoxLayout, QLabel, QApplication, QProgressBar, QDialog

    import argparse

    def parse_args():
        parser = argparse.ArgumentParser(description='ProgressBar example')
        parser.add_argument('-n', '--nb_sections', type=int, help='Number of sections in progress bar', default=500)
        parser.add_argument('-s', '--smooth_wondow', type=int, help='Window size over bars to smooth speed', default=1)
        parser.add_argument('-l', '--loop_nb_elements', type=int, help='Number of elements to simulate', default=1000)

        args = parser.parse_args()

        return args.nb_sections, args.smooth_wondow, args.loop_nb_elements

    nb_sections, smooth_wondow, loop_nb_elements = parse_args()

    class WorkerThread(QThread):
        progress_updated = pyqtSignal(int)
        _value = 100

        @classmethod
        def init(cls, value):
            cls._value = value

        def run(self):
            for i in range(self._value):
                time.sleep(randint(5,10)/self._value)  # simulate some work
                self.progress_updated.emit(i)

    class MainWindow(QDialog):
        def __init__(self,nb_sections, smooth_wondow, loop_nb):
            super().__init__()
            self.setWindowTitle("QThread Example")

            layout = QVBoxLayout()
            self.bg = SpeedProgressBar(nb_sections=nb_sections, smooth_window=smooth_wondow)
            self.bg.init(loop_nb)
            layout.addWidget(self.bg)

            self.setLayout(layout)

            # set up the worker thread
            WorkerThread.init(loop_nb)
            self.worker_thread = WorkerThread()
            self.worker_thread.progress_updated.connect(self.bg.update_bar)
            self.worker_thread.finished.connect(self.handle_thread_finished)

            # start the worker thread
            self.worker_thread.start()

        def handle_thread_finished(self):
            print("Worker thread finished.")
            #QApplication.quit()


    app = QApplication(sys.argv)
    window = MainWindow(*parse_args())
    window.show()
    sys.exit(app.exec_())


