# -*- coding: utf-8 -*-`
#  Copyright (c) Sophia Antipolis-Méditerranée, University of Cambridge 2023.
#  Authors: Kacper Pluta <kacper.pluta@inria.fr>, Alwyn Mathew <am3156@cam.ac.uk>
#  This file cannot be used without a written permission from the author(s).

import argparse
from datetime import datetime

try:
    from DTP_config import DTPConfig
except ModuleNotFoundError:
    import sys

    sys.path.insert(0, "../")
    from DTP_config import DTPConfig

from DTP_API import DTPApi
import helpers
from helpers import logger_global


def parse_args():
    """
    Get parameters from user
    """
    parser = argparse.ArgumentParser(description='Create as-built from as-designed node')
    parser.add_argument('--config_path', '-x', type=str, help='path to config file', default='../DTP_config.yaml')
    parser.add_argument('--simulation', '-s', default=False, action='store_true')

    return parser.parse_args()


if __name__ == "__main__":
    logger_global.info('New session has been started.')
    args = parse_args()
    dtp_config = DTPConfig(args.config_path)
    dtp_api = DTPApi(dtp_config, simulation_mode=args.simulation)

    elements = dtp_api.query_all_pages(dtp_api.fetch_nodes_with_element_type, dtp_config.get_ontology_uri('Wall'),
                                       "asdesigned")

    for element in elements['items']:
        asbuild_iri = helpers.create_as_performed_iri(element['_iri'])
        timestamp = helpers.get_timestamp_dtp_format(datetime.now())
        element_type = dtp_config.get_ontology_uri('Wall')
        dtp_api.create_asbuilt_node(asbuild_iri, 100, timestamp, element_type, element['_iri'])
