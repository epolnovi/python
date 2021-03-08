import datetime

class Logging:

    # _logfile = ""
    # _use_log_file = True
    # _verbose_to_terminal=False



# set_logging: Future use: add snmp trap, scom
# TODO: See if @property works better in python 3.9. in 3.8 it doesn't work on class methods


    @classmethod
    def set_logging(cls, logfile="bla.log", use_logfile=True, verbose_to_terminal=False):
        cls.logfile = logfile
        cls.use_logfile = use_logfile
        cls.verbose_to_terminal = verbose_to_terminal
    @property
    def logfile(cls):
        return cls._logfile

    @staticmethod
    def log_output(logstring):
        if Logging.use_logfile == True:
            try:
                f = open(Logging.logfile, 'a')
                timestamp = str(datetime.datetime.utcnow().isoformat(timespec='seconds', sep=' '))
                f.write(timestamp + ' ' + logstring + '\n')
                f.close
            except OSError as e:
                print('Can not write to logfile !')
                print(str(e))

        if Logging.verbose_to_terminal == True:
            print (logstring)

# Logging.set_logging(logfile="bla.log",use_logfile=True, verbose_to_terminal=False)
# Logging.log_output("blaaa")