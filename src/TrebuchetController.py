import TrebuchetView


class TrebuchetController:
    def __init__(self):
        #  Globals
        self.view = TrebuchetView.Launcher()
        self._startView()

    def _startView(self):
        self.view.run()