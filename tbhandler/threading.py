import os

import tbhandler
from threading import * # Lock, .. for modules that use this module

notify_mutex = Lock()


class Thread(Thread):
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
    def __init__(self, methods, *args, **kwargs):
        if type(methods) == list:
            self.threads = [Thread(m).start() for m in methods]
        else:
            self.threads = [Thread(methods, *arg, **kwargs).start() for arg in zip(*args)]

    def join(self):
        for t in self.threads:
            t.join()
