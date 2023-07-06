# -*- coding: utf-8 -*-`

#  Copyright (c) Centre Inria d'Université Côte d'Azur, University of Cambridge 2023.
#  Authors: Kacper Pluta <kacper.pluta@inria.fr>, Alwyn Mathew <am3156@cam.ac.uk>
#  This file cannot be used without a written permission from the author(s).

import logging
import logging.config
import multiprocessing
import os
from datetime import datetime

try:
    from DTP_config import DTPConfig
except ModuleNotFoundError:
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from DTP_config import DTPConfig


class Tupperware(dict):
    MARKER = object()

    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError('expected dict')

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, Tupperware):
            value = Tupperware(value)
        super(Tupperware, self).__setitem__(key, value)

    def __getitem__(self, key):
        found = self.get(key, Tupperware.MARKER)
        if found is Tupperware.MARKER:
            found = Tupperware()
            super(Tupperware, self).__setitem__(key, found)
        return found

    __setattr__, __getattr__ = __setitem__, __getitem__


def get_element_type(DTP_CONFIG, element):
    """
    The function returns element type. Only type fields defined in XML are recognized.

    Parameters
    ----------
    element : dictionary, obligatory
        an element

    Returns
    ------
    str
        element type
    """

    # ifc classes and old hasElementType
    for key in DTP_CONFIG.get_object_type_classes():
        if key in element.keys():
            return element[key]

    # if not found then search for the correctly defined type
    for edge in element['_outE']:
        if edge['_label'] == DTP_CONFIG.get_ontology_uri('hasElementType'):
            return edge['_targetIRI']

    raise Exception("Element is of a type class not recognized by the system.")


def get_timestamp_dtp_format(datedata):
    """
    The function returns timestamp in the format used by DTP

    Returns
    ------
    str
        timestamp
    """
    return datedata.isoformat(sep="T", timespec="seconds")


def convert_str_dtp_format_datetime(strdate):
    """
    The function returns timestamp in the format used by DTP

    Returns
    ------
    str
        timestamp
    """
    if len(strdate.strip()) != 0:
        return datetime.fromisoformat(strdate)
    else:
        Exception('Empty string cannot be converted.')


def get_info_from_log(line, marker):
    """
    Extract info from log lines

    Parameters
    ----------
    line: str
        Log line
    marker: str
        Log marker

    Returns
    -------
    list
        List of each info

    """
    index = line.find(marker)
    ids = line[index + len(marker) + 1:].strip()
    if '[' in line:
        str_1, str_2 = ids.split(',', 1)
        list_str = (str_2.strip().split('[', 1)[1].split(']')[0]).split(',')
        return [str_1, list_str]
    else:
        return [x.strip() for x in ids.split(',')]


iri_map = {'ifc': 'asbuilt',
           'task': 'action',
           'activity': 'operation',
           'workpackage': 'construction'}


def create_as_performed_iri(as_planned_iri):
    """
    Create as-performed iri from as-planned iri

    Parameters
    ----------
    as_planned_iri: str, obligatory
        an as-planned valid IRI

    Returns
    -------
    str
        Returns as-performed iri
    """
    base_uri, as_planned_node_id = as_planned_iri.rsplit('/', 1)
    asperf_substr = [k for k in iri_map.keys() if k in as_planned_node_id]
    if len(asperf_substr) == 1:
        as_perf_node_id = as_planned_node_id.replace(asperf_substr[0], iri_map[asperf_substr[0]])
        return os.path.join(base_uri, as_perf_node_id)
    else:
        raise Exception(f"{as_planned_iri} cannot be converted to as-performed iri")


def read_ply_collection_date(ply_path):
    """
    Read acquisition data from ply files

    Parameters
    ----------
    ply_path: str
        path to ply files

    Returns
    -------
        returns date
    """
    comment_date_begin = 'acquisition date'
    file = open(ply_path, 'r')
    collection_date = ''
    for line in file:
        lstrip = line.strip()
        idx = lstrip.find(comment_date_begin)
        if idx >= 0:
            collection_date = lstrip[idx + len(comment_date_begin) + 1:].strip()
        if lstrip == 'end_header':
            break
    file.close()
    if len(collection_date) == 0:
        raise Exception("The PLY file is missing the acquisition date in the format: comment collected YYYY-MM-DD")
    return datetime.strptime(collection_date, '%Y-%m-%d')


def create_logger(log_filename, formatter, level):
    """
    Multi-processing logger. Based on function from
    https://stackoverflow.com/questions/641420/how-should-i-log-while-using-multiprocessing-in-python

    Parameters
    ----------
    log_filename: str
        path to the log file
    formatter: obj
        logging formatter
    level: obj
        debug level

    Returns
    -------
        logger object
    """

    logger = multiprocessing.get_logger()
    logger.setLevel(level)
    handler = logging.FileHandler(log_filename)
    handler.setFormatter(formatter)

    # this bit will make sure you won't have 
    # duplicated messages in the output
    if not len(logger.handlers):
        logger.addHandler(handler)
    return logger


def create_logger_global(log_dir):
    """
    Create global logger

    Parameters
    ----------
    log_dir: str
        Path to the log directory

    Returns
    -------
        logger object
    """
    log_filename = os.path.join(log_dir, 'global.log')
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    return create_logger(log_filename, formatter, logging.DEBUG)


if os.path.exists('../DTP_config.yaml'):
    dtp_config = DTPConfig('../DTP_config.yaml')
elif os.path.exists(os.path.join(os.path.dirname(__file__), 'DTP_config.yaml')):
    dtp_config = DTPConfig(os.path.join(os.path.dirname(__file__), 'DTP_config.yaml'))
else:
    raise Exception("DTP_config.yaml not found!")

globals()['logger_global'] = create_logger_global(dtp_config.get_log_path())
