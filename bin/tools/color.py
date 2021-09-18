import sys


class Msg:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def warn(cls, msg):
        if 'End' in msg:
            print(cls.WARNING+msg+cls.ENDC+'\n\n')
        else:
            print(cls.WARNING+msg+cls.ENDC)

    @classmethod
    def success(cls, msg):
        print(cls.OKGREEN+msg+cls.ENDC)

    @classmethod
    def fail(cls, msg):
        print(cls.FAIL+msg+cls.ENDC)
        sys.exit(1)