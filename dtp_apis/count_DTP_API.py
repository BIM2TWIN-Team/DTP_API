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

import json


class CountAPI:
    """
    Mixin count API class contains all count methods.

    Methods
    -------
    activity_count_connected_task_nodes(activity_node_iri)
        returns dictionary created from JSON
    asdesigned_count_connected_asbuilt_nodes(node_iri)
        returns dictionary created from JSON
    asbuilt_count_connected_geomdefect_nodes(asbuilt_node_iri)
        returns dictionary created from JSON
    """

    def activity_count_connected_task_nodes(self, activity_node_iri):
        """
        The method counts task nodes connected to a node identified by activity_node_iri

        Parameters
        ----------
        activity_node_iri : str, obligatory
            a valid IRI of a node.

        Returns
        ------
        int
            return the number of task nodes connected to the node identified by activity_node_iri
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": activity_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('hasTask'): {
                    "$alias": "hasTask"
                }
            },
                {
                    "$alias": "hasTask",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('task'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "hasTask"
        })

        output = self.post_general_request(payload=payload, url=self.DTP_CONFIG.get_api_url('count_nodes'))
        return int(output.json()['total_items'])

    def asdesigned_count_connected_asbuilt_nodes(self, node_iri):
        """
        The method counts as-built nodes connected to a node identified by node_iri

        Parameters
        ----------
        node_iri : str, obligatory
            a valid IRI of a node.

        Raises
        ------
        It can raise an exception if the request has not been successful.

        Returns
        ------
        int
            return the number of defect nodes connected to the node identified by node_iri
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": node_iri,
                "<-" + self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'): {
                    "$alias": "asbuilt"
                }
            },
                {
                    "$alias": "asbuilt",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('classElement'),
                        "$inheritance": True
                    },
                    self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): False
                }
            ],
            "edge": True,
            "return": "asbuilt"
        })

        output = self.post_general_request(payload=payload, url=self.DTP_CONFIG.get_api_url('count_nodes'))
        return int(output.json()['total_items'])

    def asbuilt_count_connected_geomdefect_nodes(self, asbuilt_node_iri):
        """
        The method counts defect nodes connected to a node identified by node_iri

        Parameters
        ----------
        asbuilt_node_iri : str, obligatory
            a valid IRI of a node.

        Raises
        ------
        It can raise an exception if the request has not been successful.

        Returns
        ------
        int
            return the number of defect nodes connected to the node identified by node_iri
        """

        payload = json.dumps({
            "query": [{
                "$domain": self.DTP_CONFIG.get_domain(),
                "$iri": asbuilt_node_iri,
                "->" + self.DTP_CONFIG.get_ontology_uri('hasGeometricDefect'): {
                    "$alias": "defect"
                }
            },
                {
                    "$alias": "defect",
                    "$domain": self.DTP_CONFIG.get_domain(),
                    "$classes": {
                        "$contains": self.DTP_CONFIG.get_ontology_uri('GeometricDefect'),
                        "$inheritance": True
                    }
                }
            ],
            "edge": True,
            "return": "defect"
        })

        output = self.post_general_request(payload=payload, url=self.DTP_CONFIG.get_api_url('count_nodes'))
        return int(output.json()['total_items'])
