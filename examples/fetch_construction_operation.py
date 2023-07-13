# -*- coding: utf-8 -*-`

#  Copyright (c) Centre Inria d'Université Côte d'Azur, University of Cambridge 2023.
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
    parser = argparse.ArgumentParser(
        description='Fetch operation nodes connected to a node identified by constr_node_iri')
    parser.add_argument('--config_path', '-x', type=str, help='path to config file', default='../DTP_config.yaml')
    parser.add_argument('--simulation', '-s', default=False, action='store_true')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    dtp_config = DTPConfig(args.config_path)
    dtp_api = DTPApi(dtp_config, simulation_mode=args.simulation)
    response = dtp_api.fetch_constr_connected_oper_nodes(
        "http://bim2twin.eu/mislata_wp3/construction91227950")
    print('Response:\n', response)
