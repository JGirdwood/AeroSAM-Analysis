import numpy as np
import cPickle as Pickle
from AirborneParticleAnalysis import common


def import_level1(level1_path):
    with open(level1_path) as level1_file:
        level1_data = Pickle.load(level1_file)
    return level1_data


def fetch_row(altitude=None, time=None, level1_data=None):

    if "SUAData" in str(type(level1_data)):
        try:
            key_col = level1_data.alt
            if not isinstance(key_col, np.ndarray):
                try:
                    key_col = np.asarray(key_col)
                except(ValueError, TypeError):
                    raise TypeError("ERROR: Incompatible data type")
            row_value = altitude
            prof_mask = level1_data.up_profile_mask
            (r, cols) = prof_mask.shape
            rows = []
            for i in range(cols):
                diff_col = np.multiply(abs(key_col - row_value) - 100000000, np.reshape(prof_mask[:, i], (r, 1)))
                min_diff = np.amin(diff_col)
                min_diff_index = np.where(diff_col == min_diff)
                buf = key_col[min_diff_index[0][0]][0]
                rows.append(buf)
        except AttributeError:
            raise AttributeError("ERROR: level1_data object problem")

    elif ("StaticCASData" in str(type(level1_data))) or ("StaticFSSPData" in str(type(level1_data))):
        try:
            key_col = level1_data.time
            if not isinstance(key_col, np.ndarray):
                try:
                    key_col = np.asarray(key_col)
                except(ValueError, TypeError):
                    raise TypeError("ERROR: Incompatible data type")
            row_value = time
            rows = []
            diff_col = abs(key_col - row_value)
            min_diff = np.amin(diff_col)
            min_diff_index = np.where(diff_col == min_diff)
            buf = key_col[min_diff_index[0][0]][0]
            rows.append(buf)
        except AttributeError:
            raise AttributeError("ERROR: level1_data object problem")

    else:
        raise ValueError("ERROR: Unrecognised data object")

    return rows


def fetch_row_tolerance(altitude=None, time=None, level1_data=None):

    if "SUAData" in str(type(level1_data)):
        try:
            key_col = level1_data.alt
            tol = float(common.read_setting("height_mean_tolerance_metres"))*1000.0
            if not isinstance(key_col, np.ndarray):
                try:
                    key_col = np.asarray(key_col)
                except(ValueError, TypeError):
                    raise TypeError("ERROR: Incompatible data type")
            row_value = altitude
            prof_mask = level1_data.up_profile_mask
            (r, cols) = prof_mask.shape
            rows = []
            for i in range(cols):
                diff_col_l = \
                    np.multiply(abs(key_col - (row_value-tol)) - 100000000, np.reshape(prof_mask[:, i], (r, 1)))
                min_diff_l = np.amin(diff_col_l)
                min_diff_index_l = np.where(diff_col_l == min_diff_l)

                diff_col_u = \
                    np.multiply(abs(key_col - (row_value+tol)) - 100000000, np.reshape(prof_mask[:, i], (r, 1)))
                min_diff_u = np.amin(diff_col_u)
                min_diff_index_u = np.where(diff_col_u == min_diff_u)

                buf = list(key_col[min_diff_index_l[0][0]:min_diff_index_u[0][0]].flatten())

                rows.append(buf)
        except AttributeError:
            raise AttributeError("ERROR: level1_data object problem")

    elif ("StaticCASData" in str(type(level1_data))) or ("StaticFSSPData" in str(type(level1_data))):
        try:
            key_col = level1_data.time
            tol = float(common.read_setting("time_mean_tolerance_seconds"))
            if not isinstance(key_col, np.ndarray):
                try:
                    key_col = np.asarray(key_col)
                except(ValueError, TypeError):
                    raise TypeError("ERROR: Incompatible data type")
            row_value = time
            rows = []

            diff_col_l = abs(key_col - (row_value - tol))
            min_diff_l = np.amin(diff_col_l)
            min_diff_index_l = np.where(diff_col_l == min_diff_l)

            diff_col_u = abs(key_col - (row_value + tol))
            min_diff_u = np.amin(diff_col_u)
            min_diff_index_u = np.where(diff_col_u == min_diff_u)

            buf = list(key_col[min_diff_index_l[0][0]:min_diff_index_u[0][0]].flatten())

            rows.append(buf)
        except AttributeError:
            raise AttributeError("ERROR: level1_data object problem")

    else:
        raise ValueError("ERROR: Unrecognised data object")

    return rows


def mean_dn_dlogdp(level1_data, rows):

    if isinstance(rows[0], list):
        raise ValueError("ERROR: Pass only one profile into function")

    data_arr = np.zeros([len(rows), len(level1_data.dn_dlogdp[rows[0]])])
    (r, c) = data_arr.shape
    for i in range(r):
        for j in range(c):
            data_arr[i, j] = level1_data.dn_dlogdp[rows[i]][j]

    dn_mean = np.mean(data_arr, axis=0)

    return dn_mean


def get_time_from_alt(sua_data, alt_exact):

    if ("StaticCASData" in str(type(sua_data))) or ("StaticFSSPData" in str(type(sua_data))):
        raise ValueError("ERROR: Only SAM data can be input into this function")

    alt = sua_data.alt
    row = np.where(alt == alt_exact)[0]
    start_time = common.hhmmss_to_sec(sua_data.datetime[-6:])
    time = sua_data.time

    time_offset = time[row]

    if (time_offset - time[row-1]) < 0:
        time_offset = time[row-1]

    time_offset = time_offset[0]

    row_ref = time[0]
    if (row_ref - 1000000) < 0:
        row_ref = time[1]

    time_offset_corrected = time_offset - row_ref

    return int(start_time + time_offset_corrected[0])
