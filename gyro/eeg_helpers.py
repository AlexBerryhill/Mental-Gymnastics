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

def hjorth_params(signal):
    """Calculate Hjorth mobility and complexity"""
    diff_signal = np.diff(signal)
    diff2_signal = np.diff(diff_signal)
    var_zero = np.var(signal)
    var_d1 = np.var(diff_signal)
    var_d2 = np.var(diff2_signal)
    
    mobility = np.sqrt(var_d1 / var_zero) if var_zero != 0 else 0
    complexity = np.sqrt(var_d2 / var_d1) / mobility if var_d1 != 0 else 0
    return mobility, complexity

def spectral_entropy(psd):
    """Compute spectral entropy"""
    psd_norm = psd / np.sum(psd)  # Normalize power spectral density
    return entropy(psd_norm)