# Emulation

STA_IF = 1


class WLAN:
    def __init__(self, mode):
        self._cntdn = 4

    def active(self, enabled):
        ...

    def scan(self):
        return ((b"MyNetwork", b"123456", 11, 100, 3, 0),)

    def connect(self, ssid, pswd):
        ...

    def disconnect(self):
        ...

    def isconnected(self):
        self._cntdn -= 1
        return self._cntdn < 0
