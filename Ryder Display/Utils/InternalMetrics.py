from collections import deque

from Utils.Singleton import Singleton

class InternalMetrics(object, metaclass=Singleton):
    metrics = None
    _settings = []

    def setSettings(self, settings, log_n):
        self._settings = settings
        self._log_n = log_n

    def _fillMetrics(self, status, metrics):
        for key in status.keys():
            if isinstance(status[key], dict):
                if key not in metrics:
                    metrics[key] = {}
                self._fillMetrics(status[key], metrics[key])
            else:
                if key not in metrics:
                    metrics[key] = deque(maxlen=self._log_n)
                metrics[key].append(status[key])

    def update(self, status):
        self.metrics = {} if self.metrics == None else self.metrics
        # Process regular metrics
        self._fillMetrics(status, self.metrics)
        # Process custom metrics
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
            name = '*' + self._settings[i]['name']
            if name not in self.metrics:
                self.metrics[name] = deque(maxlen=self._log_n)
            self.metrics[name].append(value)
        return