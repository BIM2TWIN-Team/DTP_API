# -*- coding: utf-8 -*-`
#  Copyright (c) Sophia Antipolis-Méditerranée, University of Cambridge 2023.
#  Authors: Kacper Pluta <kacper.pluta@inria.fr>, Alwyn Mathew <am3156@cam.ac.uk>
#  This file cannot be used without a written permission from the author(s).

import argparse

try:
    from DTP_config import DTPConfig
except ModuleNotFoundError:
    import sys

    sys.path.insert(0, "../")
    from DTP_config import DTPConfig

from DTP_API import DTPApi


def parse_args():
    """
    Get parameters from user
    """
    parser = argparse.ArgumentParser(description='Fetch all element with element type')
    parser.add_argument('--config_path', '-x', type=str, help='path to config file', default='../DTP_config.yaml')
    parser.add_argument('--simulation', '-s', default=False, action='store_true')
    parser.add_argument('--node_type', '-n', type=str, choices=['asbuilt', 'asdesigned', 'all'],
                        help='type of nodes to be updated', default='asdesigned')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    dtp_config = DTPConfig(args.config_path)
    dtp_api = DTPApi(dtp_config, simulation_mode=args.simulation)
    response = dtp_api.query_all_pages(dtp_api.fetch_nodes_with_element_type, dtp_config.get_ontology_uri('Wall'),
                                       args.node_type)
    print('Response:\n', response)
