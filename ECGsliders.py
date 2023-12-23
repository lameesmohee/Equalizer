import numpy as np
def handle_ecg_slider(file_name, list_of_modes):
    if file_name == "VTnew (1).wav":
        list_of_modes[2]['VT'] = np.array([1, 5, -1, -5])
        list_of_modes[2]['APC'] = np.array([1000, 1500, -1000, -1500])
        list_of_modes[2]['AF'] = np.array([25, 250, -25, -250])
        return list_of_modes
    else:
        if file_name == "AF.wav":
            list_of_modes[2]['AF'] = np.array([25, 250, -25, -250])
            list_of_modes[2]['VT'] = np.array([1500, 2000, -1500, -2000])
            list_of_modes[2]['APC'] = np.array([1000, 1500, -1000, -1500])
            return list_of_modes
        else:
            if file_name == "APC_New.wav":
                list_of_modes[2]['APC'] = np.array([7, 13, -7, -13])
                list_of_modes[2]['AF'] = np.array([25, 250, -25, -250])
                list_of_modes[2]['VT'] = np.array([1500, 2000, -1500, -2000])
                return list_of_modes
            else:
                if file_name == "Normal.wav":
                    list_of_modes[2]['APC'] = np.array([1000, 1500, -1000, -1500])
                    list_of_modes[2]['AF'] = np.array([25, 250, -25, -250])
                    list_of_modes[2]['VT'] = np.array([1500, 2000, -1500, -2000])
                    return list_of_modes

            