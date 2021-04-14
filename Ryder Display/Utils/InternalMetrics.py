from Utils.Singleton import Singleton

class InternalMetrics(object, metaclass=Singleton):
    metrics = {}
    _settings = []

    def __init__(self):
        # Unused
        return

    def setSettings(self, settings):
        self._settings = settings
        for i in range(0, len(settings)):
            self.metrics[self._settings[i]['name']] = 0

    def update(self, status):
        for i in range(0, len(self._settings)):
            # Set initial value
            if self._settings[i]['operator'] == "M":
                value = -999999
            elif self._settings[i]['operator'] == "m":
                value = 999999
            elif self._settings[i]['operator'] == "+":
                value = 0
            # Compute value
            for m in range(0, len(self._settings[i]['metrics'])):
                if self._settings[i]['metrics'][m][0][0] == "*":
                    val = self.metrics[self._settings[i]['metrics'][m][0]]
                else:
                    val = status
                    for s in range(0, len(self._settings[i]['metrics'][m])):
                        if self._settings[i]['metrics'][m][s] in val:
                            val = val[self._settings[i]['metrics'][m][s]]
                        else:
                            val = 0
                            break
                if self._settings[i]['operator'] == "M":
                    value = max(value, val)
                elif self._settings[i]['operator'] == "m":
                    value = min(value, val)
                elif self._settings[i]['operator'] == "+":
                    value += val
            # Store value
            self.metrics[self._settings[i]['name']] = value

    def _getValue(self):
        return
