# -*- coding: utf-8 -*-`

#  Copyright (c) Centre Inria d'Université Côte d'Azur, University of Cambridge 2023.
#  Authors: Kacper Pluta <kacper.pluta@inria.fr>, Alwyn Mathew <am3156@cam.ac.uk>
#
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA


import logging
import logging.config
import multiprocessing
import os
import time
from datetime import datetime

try:
    from DTP_config import DTPConfig
except ModuleNotFoundError:
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    from DTP_config import DTPConfig


def get_element_type(DTP_CONFIG, element):
    """
    The function returns element type.

    Parameters
    ----------
    element : dictionary, obligatory
        an element

    Returns
    ------
    str
        element type
    """

    # search over classes with exception to the base element type
    for eclass in element['_classes']:
        if eclass != DTP_CONFIG.get_ontology_uri('classElement'):
            return eclass

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
    base_uri, node_id = as_planned_iri.rsplit('/', 1)
    asplanned_substr = [k for k in iri_map.keys() if k in node_id]
    if len(asplanned_substr) == 1:
        as_perf_node_id = node_id.replace(asplanned_substr[0], iri_map[asplanned_substr[0]])
        return f"{base_uri}/{as_perf_node_id}"
    elif len(asplanned_substr) > 1:
        raise Exception(f"{as_planned_iri} cannot be converted to as-performed iri")
    else:
        return f"{base_uri}/asbuilt_{node_id}"


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
    log_filename = os.path.join(log_dir, f"global-{time.strftime('%Y%m%d-%H%M%S')}.log")
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    return create_logger(log_filename, formatter, logging.DEBUG)


if os.path.exists('../DTP_config.xml'):
    dtp_config = DTPConfig('../DTP_config.xml')
elif os.path.exists(os.path.join(os.path.dirname(__file__), 'DTP_config.xml')):
    dtp_config = DTPConfig(os.path.join(os.path.dirname(__file__), 'DTP_config.xml'))
else:
    raise Exception("DTP_config.xml not found!")

globals()['logger_global'] = create_logger_global(dtp_config.get_log_path())
