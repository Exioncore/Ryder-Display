from Utils.Singleton import Singleton

class InternalMetrics(object, metaclass=Singleton):
    metrics = {}
    _settings = []

    def setSettings(self, settings):
        self.metrics = {}
        self._settings = settings
        for i in range(0, len(settings)):
            self.metrics[self._settings[i]['name']] = 0

    def update(self, status):
        for i in range(0, len(self._settings)):
            # Set initial value
            if self._settings[i]['operator'] == "M":
                value = float('-inf')
            elif self._settings[i]['operator'] == "m":
                value = float('inf')
            elif self._settings[i]['operator'] == "+":
                value = 0
            elif self._settings[i]['operator'] == "d":
                first = True
            # Compute value
            for m in range(0, len(self._settings[i]['metrics'])):
                if self._settings[i]['metrics'][m][0][0] == "*":
                    val = self.metrics[self._settings[i]['metrics'][m][0][1:]]
                else:
                    val = status
                    for s in range(0, len(self._settings[i]['metrics'][m])):
                        if self._settings[i]['metrics'][m][s] in val:
                            val = val[self._settings[i]['metrics'][m][s]]
                        else:
                            if self._settings[i]['operator'] == "M":
                                val = float('-inf')
                            elif self._settings[i]['operator'] == "m":
                                val = float('inf')
                            elif self._settings[i]['operator'] == "+":
                                val = 0
                            elif self._settings[i]['operator'] == "d":
                                val = 0
                            break
                if self._settings[i]['operator'] == "M":
                    value = max(value, val)
                elif self._settings[i]['operator'] == "m":
                    value = min(value, val)
                elif self._settings[i]['operator'] == "+":
                    value += val
                elif self._settings[i]['operator'] == "d":
                    if first == True:
                        value = val
                        first = False
                    else:
                        value -= val
                        break
            # Store value
            self.metrics[self._settings[i]['name']] = value
