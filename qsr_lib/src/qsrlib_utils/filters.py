# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
from qsrlib_io.world_qsr_trace import World_QSR_Trace


def apply_median_filter(qsr_world, params):
    """
    Function to apply a median filter to the QSRLib World Trace
    ..seealso:: For further details about Filters, refer to its :doc:`description. <../handwritten/filters/>`


    :param qsr_world: A World_QSR_Trace object containing the data to be filtered
    :type qsrlib_io.World_QSR_Trace
    :param params: A dictionary with key = "window" and value as an int
    :type dict

    :return: A World_QSR_Trace object containing the filtered data
    :rtype: qsrlib_io.World_QSR_Trace
    """
    if not isinstance(qsr_world, World_QSR_Trace):
        raise RuntimeError("Applying Median Filter. qsr_world should be of type qsrlib_io.World_QSR_Trace")

    frames = qsr_world.get_sorted_timestamps()
    requested_qsrs = qsr_world.qsr_type.split(",")
    # print("all frames:", len(frames))
    # print("qsrs requested:", qsr_world.qsr_type)


    # Obtain the QSR data for each object set, and each qsr type.
    obj_based_qsr_world = {}
    for frame in frames:
        for objs, qsrs in qsr_world.trace[frame].qsrs.items():
            if objs not in obj_based_qsr_world:
                obj_based_qsr_world[objs] = {}
                for qsr_type in requested_qsrs:
                    # print("adding data:", qsr_type)
                    obj_based_qsr_world[objs][qsr_type] = []
                    obj_based_qsr_world[objs][qsr_type+"_frames"] = []

            for qsr_type, qsr in qsrs.qsr.items():
                obj_based_qsr_world[objs][qsr_type].append(qsr)
                obj_based_qsr_world[objs][qsr_type+"_frames"].append(frame)


    # Apply the Median Filter to each list of QSR seperately
    for objs, data in obj_based_qsr_world.items():
        for qsr_type in requested_qsrs:
            # print("filtering:", qsr_type)
            obj_based_qsr_world[objs][qsr_type+"_filtered"] = median_filter(data[qsr_type], params["window"])


    # Overwrite the original QSR data with the filtered data, at the appropriate timepoints (merging QSR types back together in the process)
    for frame in frames:
        for objs, data in obj_based_qsr_world.items():
            new_qsrs = {}
            for qsr_type in requested_qsrs:
                if frame in data[qsr_type+"_frames"]:
                    ind = data[qsr_type+"_frames"].index(frame)
                    # print("frame:", frame, qsr_type, "index:", ind)
                    new_qsrs[qsr_type] = data[qsr_type+"_filtered"][ind]

            # print("frame:", frame, "prev:", qsr_world.trace[frame].qsrs[objs].qsr, "new:", new_qsrs)
            qsr_world.trace[frame].qsrs[objs].qsr = new_qsrs
    return qsr_world



def median_filter(data, n=3):
    """
    Function to filter over 1 dimensional data, using window of size n
    n must be odd and >2, or the tail size will be 0; and will be floor(n/2).

    :param data: one dimensional list of QSR states
    :type list
    :param n: the window the median filter is applied to
    :type int

    :return: a one dimensional list of filtered QSR states
    :rtype: list
    """

    if len(data) < n:
        #RuntimeWarning("Median Filter Window is larger than the data")
        # If ambiguity over which relation to add. Use the first.
        counts, value = count_elements_in(data)
        if counts.count(max(counts)) is 1:
            data = [value]*len(data)
        else:
            data = [data[0]]*len(data)
    else:
        #Initiate the filter using the median of the first n elements:
        tail = (n-1)/2  # This will return the floored int o
        for i in range(0, len(data)):
            #for an incomplete window, repeate the first or last elements to get a window.
            if i < tail:
                window = [data[0]]*tail
                window.extend(data[i: i+tail+1])
            # elif i+tail+1 > len(data):
            #     window = [data[-1]]*tail
            #     window.extend(data[i-tail: i+1])
            else:
                window = data[i-tail: i+tail+1]

            # If ambiguity over which relation to add. Add previous.
            counts, value = count_elements_in(window)
            if counts.count(max(counts)) is 1:
                data[i] = value
            else:
                # ambiguous - adding previous state
                data[i] = data[i-1]
    return data

def count_elements_in(data):
    counts, values = [], []
    elms = [p for p in data]

    for x in set(elms):
        counts.append(elms.count(x))
        values.append(x)
        value = values[np.argmax(counts)]
    return counts, value