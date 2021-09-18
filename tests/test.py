import sys

arg = sys.argv[1]
if arg:
    if arg.split('=')[0] == '-n':
        node_list = arg.split('=')[1].split(',')
    else:
        pass
else:
