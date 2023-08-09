class State:

    def __init__(self):
        self.gs = {}


    def getState(self, key=None):
        if key:
            return self.gs[key]
        return self.gs

    def updateState(self, key, val):
        self.gs[key] = val



