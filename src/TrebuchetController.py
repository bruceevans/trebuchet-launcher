import TrebuchetView


class TrebuchetController:
    def __init__(self):

        #  Globals
        self.view = TrebuchetView.Launcher(self)
        self._startView()

        print("On Screen")

    def _startView(self):
        self.view.run()

    ## Tag specific methods ##

    #  Get tags from json file
    def _getTags(self):
        tags = []
        return tags

    def _addTag(self, tag):
        pass

    def _removeTag(self, tag):
        pass

    ## JSON specific methods ##

    def _getJsonData(self, tag):
        # go through the json file and get the values with the tag
        # data = []
        # return data
        pass

    ## Settings specific methods ##

# needs reference to both view and model