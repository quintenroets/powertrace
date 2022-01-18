import os

import tbhandler
import threading

notify_mutex = threading.Lock()


class Thread(threading.Thread):
    handled = False
    
    def __init__(self, target, *args, exit_on_error=True, **kwargs):
        self.exit_on_error = exit_on_error
        super(Thread, self).__init__(target=self.start_verbose, args=(target, *args), kwargs=(kwargs))
        
    def start_verbose(self, target, *args, **kwargs):
        try:
            target(*args, **kwargs)
        except:
            with notify_mutex:
                if not self.handled:
                    self.handled = True
                    tbhandler.show()
                    if self.exit_on_error:
                        os._exit(0)

    def start(self):
        super(Thread, self).start()
        return self

    def join(self):
        super(Thread, self).join()


class Threads:
    def __init__(self, method, *args, **kwargs):
        if callable(method):
            self.threads = [Thread(method, *arg, **kwargs).start() for arg in zip(*args)]
        else:
            self.threads = [Thread(m).start() for m in method]

    def join(self):
        for t in self.threads:
            t.join()
