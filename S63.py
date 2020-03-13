from modules.automate.automate import Automate
import signal
import sys


class S63:
    Automate = None

    def __init__(self):
        print ("[STARTUP]")

        signal.signal(signal.SIGINT, self.OnSignal)

        self.Automate = Automate()

    def OnSignal(self, signal, frame):
        print "[SIGNAL] Shutting down on %s" % signal
        sys.exit(0)


def main():
    print "[main]"
    TDaemon = S63()


if __name__ == "__main__":
    main()
