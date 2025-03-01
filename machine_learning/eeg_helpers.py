from pylsl import resolve_streams, resolve_byprop

def resolve_stream(*args):
    if len(args) == 0:
        return resolve_streams()
    elif type(args[0]) in [int, float]:
        return resolve_streams(args[0])
    elif type(args[0]) is str:
        if len(args) == 1:
            return resolve_bypred(args[0])
        elif type(args[1]) in [int, float]:
            return resolve_bypred(args[0], args[1])
        else:
            if len(args) == 2:
                return resolve_byprop(args[0], args[1])
            else:
                return resolve_byprop(args[0], args[1], args[2])
