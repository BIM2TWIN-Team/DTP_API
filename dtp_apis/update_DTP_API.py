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
import os

from helpers import logger_global


class UpdateAPI:
    """
    Mixin update API class contains update node functions.

    Methods
    -------
    update_asdesigned_param_node(node_iri, is_as_designed)
        returns bool, True if success and False otherwise
    update_operation_node(per_node_iri, list_of_action_iri, process_start, process_end, log_path)
        returns bool, True if success and False otherwise
    update_construction_node(constr_iri, list_of_operation_iri, log_path)
        returns bool, True if success and False otherwise
    delete_param_in_node(node_iri, field, previous_field_value=None, field_placeholder, is_revert_session)
        returns bool, True if success and False otherwise
    add_param_in_node(node_iri, field, field_value)
        returns bool, True if success and False otherwise
    """

    def update_asdesigned_param_node(self, node_iri, is_as_designed):
        """
        The method updates AsDesigned parameters in the node corresponding to given iri

        Parameters
        ----------
        node_iri: str, obligatory
            an iri of a node to be updated
        is_as_designed: bool, obligatory
            the value of AsDesigned that will be used to update the node

        Returns
        -------
        bool
            True if a blob has been node has been updated and False otherwise
        """

        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": node_iri,
            self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): is_as_designed
        }])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        f"DTP_API - UPDATE_isAsDesigned_PARAM_NODE_OPERATION: {node_iri}, {is_as_designed}")
                return True
            else:
                logger_global.error("Updating nodes failed. Response code: " + str(response.status_code))
                return False
        return True

    def update_action_node(self, task_type, action_node_iri, task_iri, target_as_built_iri, contractor,
                           process_start, process_end):
        """
        The method updates a new operation.

        Parameters
        ----------
        task_type : str, obligatory
            a valid task type.
        action_node_iri: str, obligatory
            a valid action IRI of a node.
        task_iri:
            a valid task IRI.
        target_as_built_iri: str, obligatory
            a valid iri of the as-built targets of action
        contractor: str, obligatory
            contractor from as-planned
        process_start: str, obligatory
            Start date of the action
        process_end: str, obligatory
            End date of the action

        Raises
        ------
        It can raise an exception if the request has not been successful.

        Returns
        ------
        bool
            return True if operation node has been updated and False otherwise.
        """
        # creating backup of the node
        node_info = self.fetch_node_with_iri(action_node_iri)
        dump_path = os.path.join(self.node_log_dir, f"{action_node_iri.rsplit('/')[-1]}.json")
        with open(dump_path, 'w') as fp:
            json.dump(node_info, fp)

        out_edge_dict = {}
        if target_as_built_iri:
            out_edge_dict = {
                "_label": self.DTP_CONFIG.get_ontology_uri('hasAction'),
                "_targetIRI": target_as_built_iri
            }

        query_dict = {
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": action_node_iri,
            "_outE": [out_edge_dict]
        }

        if contractor:
            query_dict[self.DTP_CONFIG.get_ontology_uri('constructionContractor')] = contractor

        if target_as_built_iri:
            query_dict["_outE"].append({
                "_label": self.DTP_CONFIG.get_ontology_uri('hasTarget'),
                "_targetIRI": target_as_built_iri
            })
        if task_iri:
            query_dict["_outE"].append({
                "_label": self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'),
                "_targetIRI": task_iri
            })

        if task_type:
            query_dict["_outE"].append({
                "_label": self.DTP_CONFIG.get_ontology_uri('hasTaskType'),
                "_targetIRI": task_type
            })

        if process_start:
            query_dict[self.DTP_CONFIG.get_ontology_uri('processStart')] = process_start

        if process_end:
            query_dict[self.DTP_CONFIG.get_ontology_uri('processEnd')] = process_end

        payload = json.dumps([query_dict])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(f"DTP_API - UPDATE_ACTION_IRI: {action_node_iri}, {dump_path}")
                return True
            else:
                logger_global.error("Updating action node failed. Response code: " + str(response.status_code))
                return False
        return True

    def update_operation_node(self, task_type, oper_node_iri, target_activity_iri, list_of_action_iri, process_start,
                              last_updated, process_end):
        """
        The method updates a new operation.

        Parameters
        ----------
        task_type : str, obligatory
            a valid task type from activity node.
        oper_node_iri : str, obligatory
            a valid IRI of a node.
        target_activity_iri : str, obligatory
            a valid activity.
        list_of_action_iri : list, optional
            list of connection actions iri.
        process_start: str, obligatory
            Start date of the operation
        last_updated: str, obligatory
            Last updated date
        process_end: str, obligatory
            End date of the operation

        Raises
        ------
        It can raise an exception if the request has not been successful.

        Returns
        ------
        bool
            return True if operation node has been updated and False otherwise.
        """
        # creating backup of the node
        node_info = self.fetch_node_with_iri(oper_node_iri)
        dump_path = os.path.join(self.node_log_dir, f"{oper_node_iri.rsplit('/')[-1]}.json")
        with open(dump_path, 'w') as fp:
            json.dump(node_info, fp)

        out_edge_to_actions = []
        if list_of_action_iri:
            # collecting already existing edges
            already_existing_edges = node_info['items'][0]['_outE']
            out_edge_to_actions = [*already_existing_edges]
            # create new out edges list of dictionaries
            for action_iri in list_of_action_iri:
                out_edge_dict = {
                    "_label": self.DTP_CONFIG.get_ontology_uri('hasAction'),
                    "_targetIRI": action_iri
                }
                out_edge_to_actions.append(out_edge_dict)

        query_dict = {
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": oper_node_iri,
            "_outE": out_edge_to_actions
        }

        if process_start:
            query_dict[self.DTP_CONFIG.get_ontology_uri('processStart')] = process_start

        if last_updated:
            query_dict[self.DTP_CONFIG.get_ontology_uri('lastUpdatedOn')] = last_updated

        if process_end:
            query_dict[self.DTP_CONFIG.get_ontology_uri('processEnd')] = process_end

        if target_activity_iri:
            query_dict["_outE"].append({
                "_label": self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'),
                "_targetIRI": target_activity_iri
            })

        if task_type:
            query_dict["_outE"].append({
                "_label": self.DTP_CONFIG.get_ontology_uri('hasTaskType'),
                "_targetIRI": task_type
            })

        payload = json.dumps([query_dict])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(f"DTP_API - UPDATE_OPERATION_IRI: {oper_node_iri}, {dump_path}")
                return True
            else:
                logger_global.error("Updating operation node failed. Response code: " + str(response.status_code))
                return False
        return True

    def update_construction_node(self, productionMethodType, constr_node_iri, workpkg_node_iri, list_of_operation_iri):
        """
        The method updates construction node.

        Parameters
        ----------
        productionMethodType : str, obligatory
            a valid production method type from corresponding work package
        constr_node_iri : str, obligatory
            a valid IRI of a node.
        workpkg_node_iri : str, obligatory
            a valid work package IRI.
        list_of_operation_iri : list, optional
            list of connected operation iri

        Raises
        ------
        It can raise an exception if the request has not been successful.

        Returns
        ------
        bool
            return True if construction node has been created and False otherwise.
        """

        # creating backup of the node
        node_info = self.fetch_node_with_iri(constr_node_iri)
        dump_path = os.path.join(self.node_log_dir, f"{constr_node_iri.rsplit('/')[-1]}.json")
        with open(dump_path, 'w') as fp:
            json.dump(node_info, fp)

        # update node if operation iri list has at least one item
        out_edge_to_operation = []
        if len(list_of_operation_iri):
            # collecting already existing edges
            already_existing_edges = node_info['items'][0]['_outE']
            out_edge_to_operation = [*already_existing_edges]
            # create new out edges list of dictionaries
            for action_iri in list_of_operation_iri:
                out_edge_dict = {
                    "_label": self.DTP_CONFIG.get_ontology_uri('hasAction'),
                    "_targetIRI": action_iri
                }
                out_edge_to_operation.append(out_edge_dict)

        query_dict = {
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": constr_node_iri,
            "_outE": out_edge_to_operation
        }

        if productionMethodType:
            query_dict["_outE"].append({
                "_label": self.DTP_CONFIG.get_ontology_uri('hasProductionMethodType'),
                "_targetIRI": productionMethodType
            })

        if workpkg_node_iri:
            query_dict["_outE"].append({
                "_label": self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'),
                "_targetIRI": workpkg_node_iri
            })

        payload = json.dumps([query_dict])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(f"DTP_API - UPDATE_CONSTRUCTION_IRI: {constr_node_iri}, {dump_path}")
                return True
            else:
                logger_global.error("Updating operation node failed. Response code: " + str(response.status_code))
                return False

    def delete_param_in_node(self, node_iri, field, previous_field_value=None, field_placeholder="delete",
                             is_revert_session=False):
        """
        The method removes a specific field from a node

        Parameters
        ----------
        node_iri: str, obligatory
            an iri of a node to act on
        field: str, obligatory
            an url or str of node field
        previous_field_value: str, optional
            previous field value
        field_placeholder: str, optional
            placeholder for the deleting field
        is_revert_session: bool, optional
            true if reverting from session file

        Returns
        -------
        bool
            True if a blob has been node has been updated and False otherwise
        """
        if not is_revert_session:
            assert previous_field_value is not None, 'previous_field_value needed for logging'
        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": node_iri,
            field: field_placeholder  # field_placeholder to ensure payload is valid
        }])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_unset'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        f"DTP_API - REMOVED_PARAM_NODE_OPERATION: {node_iri}, {field}, {previous_field_value} ")
                return True
            else:
                logger_global.error("Updating nodes failed. Response code: " + str(response.status_code))
                return False
        return True

    def add_param_in_node(self, node_iri, field, field_value):
        """
        The method add new parameter to the node

        Parameters
        ----------
        node_iri: str, obligatory
            an iri of a node to be updated
        field: str, obligatory
            url or str of the field name
        field_value: str, obligatory
            value of the adding field

        Returns
        -------
        bool
            True if a blob has been node has been updated and False otherwise
        """

        payload = json.dumps([{
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": node_iri,
            field: field_value
        }])

        response = self.put_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('update_set'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info(
                        f"DTP_API - ADD_PARAM_NODE_OPERATION: {node_iri}, {field}")
                return True
            else:
                logger_global.error("Updating nodes failed. Response code: " + str(response.status_code))
                return False
        return True
