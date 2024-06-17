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

from helpers import logger_global


class LinkAPI:
    """
    Mixin link API class contains all link methods.

    Methods
    -------
    link_node_element_to_blob(node_uuid, blob_uuid)
        returns bool, True if success and False otherwise
    link_node_element_to_defect(element_node_iri, defect_node_iri)
        returns bool, True if success and False otherwise
    link_node_operation_to_action(oper_node_iri, action_node_iri)
        returns bool, True if success and False otherwise
    link_node_schedule_to_constr(schedule_node_iri, constr_node_iri)
        returns bool, True if success and False otherwise
    link_node_constr_to_operation(constr_node_iri, oper_node_iri)
        returns bool, True if success and False otherwise
    """

    def link_node_element_to_blob(self, node_uuid, blob_uuid):
        """
        The method links a blob to an element.

        Parameters
        ----------
        node_uuid : str, obligatory
            a valid element UUID of an element which will be linked to a blob
        blob_uuid : str, obligatory
            a valid blob UUID

        Returns
        ------
        bool
            True if the element has been linked with a blob, and False otherwise
        """

        payload = json.dumps({
            "blob_uuid": blob_uuid,
            "avatar_uuids": [node_uuid],
            "ignore_conflicts": False
        })

        response = self.post_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('link_blob'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info("DTP_API - NEW_LINK_ELEMENT_BLOB: " + node_uuid + ', ' + blob_uuid)
                return True
            else:
                logger_global.error("Linking nodes failed. Response code: " + str(response.status_code))
                return False
        return True

    def link_node_element_to_defect(self, element_node_iri, defect_node_iri):
        """
        The method links a defect with an element.

        Parameters
        ----------
        element_node_iri : str, obligatory
            a valid element IRI of an element, which will be linked to a defect
        defect_node_iri : str, obligatory
            a valid defect's IRI

        Returns
        ------
        bool
            True if the element has been linked with a defect, and False otherwise
        """

        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": element_node_iri,
            "_outE": [{
                "_label": self.DTP_CONFIG.get_ontology_uri('hasGeometricDefect'),
                "_targetIRI": defect_node_iri
            }]
        }])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        "DTP_API - NEW_LINK_ELEMENT_DEFECT: " + element_node_iri + ', ' + defect_node_iri)
                return True
            else:
                logger_global.error("Linking nodes failed. Response code: " + str(response.status_code))
                return False
        return True

    def link_node_element_to_element_type(self, element_node_iri, element_type_iri):
        """
        The method links an element node to element type

        Parameters
        ----------
        element_node_iri : str, obligatory
            a valid element IRI of an element
        element_type_iri : str, obligatory
            a valid element type IRI

        Returns
        ------
        bool
            True if the element has been linked with an element type, and False otherwise
        """

        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": element_node_iri,
            "_outE": [{
                "_label": self.DTP_CONFIG.get_ontology_uri('hasElementType'),
                "_targetIRI": element_type_iri
            }]
        }])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        f"DTP_API - NEW_LINK_ELEMENT_ELEMENT_TYPE: {element_node_iri}, {element_type_iri}")
                return True
            else:
                logger_global.error("Linking nodes failed. Response code: " + str(response.status_code))
                return False
        return True

    def link_node_operation_to_action(self, oper_node_iri, list_of_action_iri):
        """
        The method links an action with an operation.

        Parameters
        ----------
        oper_node_iri : str, obligatory
            a valid operation IRI
        list_of_action_iri : list, optional
            list of connection actions iri

        Returns
        ------
        bool
            True if the operation has been linked with actions, and False otherwise
        """
        assert len(list_of_action_iri), "No action nodes listed"
        node_info = self.fetch_node_with_iri(oper_node_iri)
        already_existing_edges = node_info['items'][0]['_outE']

        # create out edges list of dictionaries
        out_edge_to_actions = [*already_existing_edges]
        for action_iri in list_of_action_iri:
            out_edge_dict = {
                "_label": self.DTP_CONFIG.get_ontology_uri('hasAction'),
                "_targetIRI": action_iri
            }
            out_edge_to_actions.append(out_edge_dict)

        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": oper_node_iri,
            "_outE": out_edge_to_actions
        }])

        old_out_edges = [x['_targetIRI'] for x in already_existing_edges]
        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        f"DTP_API - NEW_LINK_OPERATION_ACTION: {oper_node_iri}, {old_out_edges}")
                return True
            else:
                logger_global.error("Linking nodes failed. Response code: " + str(response.status_code))
                return False
        return True

    def link_node_schedule_to_constr(self, schedule_node_iri, constr_node_iri):
        """
        The method links a construction with a schedule.

        Parameters
        ----------
        schedule_node_iri : str, obligatory
            a valid schedule IRI
        constr_node_iri : str, obligatory
            a valid construction IRI

        Returns
        ------
        bool
            True if the element has been linked with a defect, and False otherwise
        """

        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": schedule_node_iri,
            "_outE": [{
                "_label": self.DTP_CONFIG.get_ontology_uri('hasConstruction'),
                "_targetIRI": constr_node_iri
            }]
        }])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        "DTP_API - NEW_LINK_SCHEDULE_CONSTR: " + schedule_node_iri + ', ' + constr_node_iri)
                return True
            else:
                logger_global.error("Linking nodes failed. Response code: " + str(response.status_code))
                return False
        return True

    def link_node_constr_to_operation(self, constr_node_iri, list_of_operation_iri):
        """
        The method links an operation with a construction.

        Parameters
        ----------
        constr_node_iri : str, obligatory
            a valid construction IRI
        list_of_operation_iri : list, obligatory
            list of connected operation iri

        Returns
        ------
        bool
            True if the construction has been linked with operations, and False otherwise
        """
        assert len(list_of_operation_iri), "No operation nodes listed"
        node_info = self.fetch_node_with_iri(constr_node_iri)
        already_existing_edges = node_info['items'][0]['_outE']

        # create out edges list of dictionaries
        out_edge_to_operation = [*already_existing_edges]
        for operation_iri in list_of_operation_iri:
            out_edge_dict = {
                "_label": self.DTP_CONFIG.get_ontology_uri('hasOperation'),
                "_targetIRI": operation_iri
            }
            out_edge_to_operation.append(out_edge_dict)

        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": constr_node_iri,
            "_outE": out_edge_to_operation
        }])

        old_out_edges = [x['_targetIRI'] for x in already_existing_edges]
        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        f"DTP_API - NEW_LINK_CONSTR_OPERATION: {constr_node_iri}, {old_out_edges}")
                return True
            else:
                logger_global.error("Linking nodes failed. Response code: " + str(response.status_code))
                return False
        return True

    def link_node_action_to_asbuilt(self, action_node_iri, target_asbuilt_iri):
        """
        The method links an asbuilt nodes with its action.

        Parameters
        ----------
        action_node_iri : str, obligatory
            a valid action IRI
        target_asbuilt_iri : list, obligatory
            list of connected asbuilt iri

        Returns
        ------
        bool
            True if the action has been linked with asbuilt, and False otherwise
        """
        assert target_asbuilt_iri, "No target nodes given"
        out_edge = {
            "_label": self.DTP_CONFIG.get_ontology_uri('hasTarget'),
            "_targetIRI": target_asbuilt_iri
        }

        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": action_node_iri,
            "_outE": [out_edge]
        }])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        f"DTP_API - NEW_LINK_ACTION_ASBUILT: {action_node_iri}, {target_asbuilt_iri}")
                return True
            else:
                logger_global.error("Linking nodes failed. Response code: " + str(response.status_code))
                return False
        return True
