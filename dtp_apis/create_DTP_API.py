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

import validators

from helpers import logger_global


class CreateAPI:
    """
    Mixin create API class contains all create methods.

    Methods
    -------
    create_asbuilt_node(element_iri_uri, progress, timestamp, element_type, target_iri)
        returns bool, True if success and False otherwise
    create_defect_node(defect_class, defect_node_iri, defect_criticality, timestamp, defect_type)
        returns bool, True if success and False otherwise
    create_kpi_node_defectsperwork(kpi_node_iri, task_type, value, ref_quant, sampl_quant, inter_start_date,
                                    inter_end_date)
        returns bool, True if success and False otherwise
    create_action_node(task_type, action_node_iri, task_iri, target_as_built_iri, contractor, process_start,
        process_end)
        returns bool, True if success and False otherwise
    create_operation_node(taskType, oper_node_iri, target_activity_iri, list_of_action_iri, process_start,
         process_end)
        returns bool, True if success and False otherwise
    create_construction_node(productionMethodType, constr_node_iri, workpkg_node_iri, list_of_operation_iri)
        returns bool, True if success and False otherwise
    create_kpi_zerodefectwork(kpi_node_iri, value, ref_quant, sampl_quant, inter_start_date, inter_end_date)
        returns bool, True if success and False otherwise
    """

    def create_asbuilt_node(self, element_iri_uri, progress, timestamp, element_type, target_iri):
        """
        The method creates a new As-Built element.

        Parameters
        ----------
        element_iri_uri : str, obligatory
            the full IRI of the new As-Built element
        progress : int, obligatory
            the progress in percentage of the new As-Built element
        timestamp : datetime, obligatory
            associated timestamp in the isoformat(sep="T", timespec="seconds")
        element_type : str, obligatory
            element type as defined by the ontology, normally it should be
            the same type as the type of the corresponding As-Designed element
        target_iri : str, obligatory
            the IRI of the associated element; here it should correspond to the IRI
            of the respective As-Designed element

        Raises
        ------
        It can raise an exception if the target or element IRIs are not valid URIs

        Returns
        ------
        bool
            True if the element has been created without an error, and False otherwise
        """

        if not validators.url(element_iri_uri):
            raise Exception("Sorry, the target IRI is not a valid URL.")

        if not validators.url(target_iri):
            raise Exception("Sorry, the target IRI is not a valid URL.")

        if progress == 100:
            payload = json.dumps([
                {
                    "_classes": [self.DTP_CONFIG.get_ontology_uri('classElement')],
                    "_domain": self.DTP_CONFIG.get_domain(),
                    "_iri": element_iri_uri,
                    "_visibility": 0,
                    self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): False,
                    self.DTP_CONFIG.get_ontology_uri('timeStamp'): timestamp,
                    self.DTP_CONFIG.get_ontology_uri('progress'): progress,
                    self.DTP_CONFIG.get_ontology_uri('hasGeometryStatusType'): self.DTP_CONFIG.get_ontology_uri(
                        'CompletelyDetected'),
                    "_outE": [
                        {
                            "_label": self.DTP_CONFIG.get_ontology_uri('hasElementType'),
                            "_targetIRI": element_type
                        },
                        {
                            "_label": self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'),
                            "_targetIRI": target_iri
                        }
                    ]
                }
            ])
        else:
            payload = json.dumps([
                {
                    "_classes": [self.DTP_CONFIG.get_ontology_uri('classElement')],
                    "_domain": self.DTP_CONFIG.get_domain(),
                    "_iri": element_iri_uri,
                    self.DTP_CONFIG.get_ontology_uri('isAsDesigned'): False,
                    self.DTP_CONFIG.get_ontology_uri('timeStamp'): timestamp,
                    self.DTP_CONFIG.get_ontology_uri('progress'): progress,
                    "_outE": [
                        {
                            "_label": self.DTP_CONFIG.get_ontology_uri('hasElementType'),
                            "_targetIRI": element_type
                        },
                        {
                            "_label": self.DTP_CONFIG.get_ontology_uri('intentStatusRelation'),
                            "_targetIRI": target_iri
                        }
                    ]
                }
            ])

        response = self.post_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('add_node'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info("DTP_API - NEW_ELEMENT_IRI: " + element_iri_uri)
                return True
            else:
                logger_global.error("Creating new element failed. Response code: " + str(response.status_code))
                return False
        return True

    def create_defect_node(self, defect_class, defect_node_iri, defect_criticality, timestamp, defect_type):
        """
        The method counts defect nodes connected to a node identified by node_iri

        Parameters
        ----------
        defect_class
        defect_node_iri
        defect_criticality
        timestamp
        defect_type

        Raises
        ------
        It can raise an exception if the request has not been successful.

        Returns
        ------
        int
            return True if a new defect node has been created and False otherwise.

        """

        if not validators.url(defect_node_iri):
            raise Exception("Sorry, the IRI is not a valid URL.")

        payload = json.dumps([
            {
                "_classes": [defect_class],
                "_domain": self.DTP_CONFIG.get_domain(),
                "_iri": defect_node_iri,
                "_visibility": 0,
                self.DTP_CONFIG.get_ontology_uri('timeStamp'): timestamp,
                self.DTP_CONFIG.get_ontology_uri('defect_criticality'): defect_criticality,
                "_outE": [
                    {
                        "_label": self.DTP_CONFIG.get_ontology_uri('hasDefectType'),
                        "_targetIRI": defect_type
                    }
                ]
            }
        ])

        response = self.post_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('add_node'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info("DTP_API - NEW_DEFECT_IRI: " + defect_node_iri)
                return True
            else:
                logger_global.error("Creating new element failed. Response code: " + str(response.status_code))
                return False
        return True

    def create_kpi_node_defectsperwork(self, kpi_node_iri, task_type, value, ref_quant, sampl_quant, inter_start_date,
                                       inter_end_date):

        if not validators.url(kpi_node_iri):
            raise Exception("Sorry, the IRI is not a valid URL.")

        payload = json.dumps([
            {
                "_classes": [self.DTP_CONFIG.get_ontology_uri('kpiNumberOfDefectsPerWork')],
                "_domain": self.DTP_CONFIG.get_kpi_domain(),
                "_iri": kpi_node_iri,
                "_visibility": 0,
                self.DTP_CONFIG.get_ontology_uri('kpiHasTaskType'): task_type,
                self.DTP_CONFIG.get_ontology_uri('kpiValue'): value,
                self.DTP_CONFIG.get_ontology_uri('kpiReferenceQuantity'): ref_quant,
                self.DTP_CONFIG.get_ontology_uri('kpiSampleQuantity'): sampl_quant,
                self.DTP_CONFIG.get_ontology_uri('kpiIntervalStartDate'): inter_start_date,
                self.DTP_CONFIG.get_ontology_uri('kpiIntervalEndDate'): inter_end_date,
            }
        ])

        response = self.post_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('add_node'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info("DTP_API - NEW_KPI_IRI: " + kpi_node_iri)
                return True
            else:
                logger_global.error("Creating new element failed. Response code: " + str(response.status_code))
                return False
        return True

    def create_action_node(self, action_node_iri, task_type=None, task_iri=None, target_as_built_iri=None,
                           contractor=None, process_start=None, process_end=None):
        """
        The method creates a new action.

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
            return True if a new action node has been created and False otherwise.
        """

        if not validators.url(action_node_iri):
            raise Exception("Sorry, the IRI is not a valid URL.")

        query_dict = {
            "_classes": [self.DTP_CONFIG.get_ontology_uri('asPerformedAction')],
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": action_node_iri,
            "_visibility": 0,
            "_outE": []
        }

        if contractor:
            query_dict[self.DTP_CONFIG.get_ontology_uri('constructionContractor')] = contractor

        if process_start:
            query_dict[self.DTP_CONFIG.get_ontology_uri('processStart')] = process_start

        if process_end:
            query_dict[self.DTP_CONFIG.get_ontology_uri('processEnd')] = process_end

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

        payload = json.dumps([query_dict])

        response = self.post_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('add_node'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info("DTP_API - NEW_ACTION_IRI: " + action_node_iri)
                return True
            else:
                logger_global.error("Creating new element failed. Response code: " + str(response.status_code))
                return False
        return True

    def create_operation_node(self, oper_node_iri, task_type=None, target_activity_iri=None, list_of_action_iri=None,
                              process_start=None, last_updated=None, process_end=None):
        """
        The method creates a new operation.

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
            return True if a new operation node has been created and False otherwise.
        """

        if list_of_action_iri is None:
            list_of_action_iri = []
        if not validators.url(oper_node_iri):
            raise Exception("Sorry, the IRI is not a valid URL.")

        # create out edges list of dictionaries
        out_edge_to_actions = []
        for action_iri in list_of_action_iri:
            out_edge_dict = {
                "_label": self.DTP_CONFIG.get_ontology_uri('hasAction'),
                "_targetIRI": action_iri
            }
            out_edge_to_actions.append(out_edge_dict)

        query_dict = {
            "_domain": self.DTP_CONFIG.get_domain(),
            "_classes": [self.DTP_CONFIG.get_ontology_uri('asPerformedOperation')],
            "_iri": oper_node_iri,
            "_visibility": 0,
            "_outE": [
                *out_edge_to_actions
            ]
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

        response = self.post_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('add_node'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info("DTP_API - NEW_OPERATION_IRI: " + oper_node_iri)
                return True
            else:
                logger_global.error("Creating new element failed. Response code: " + str(response.status_code))
                return False
        return True

    def create_construction_node(self, constr_node_iri, productionMethodType=None, workpkg_node_iri=None,
                                 list_of_operation_iri=None):
        """
        The method creates a new construction.

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
            return True if a new construction node has been created and False otherwise.
        """

        if list_of_operation_iri is None:
            list_of_operation_iri = []
        if not validators.url(constr_node_iri):
            raise Exception("Sorry, the IRI is not a valid URL.")

        # create out edges list of dictionaries
        out_edge_to_operation = []
        for operation_iri in list_of_operation_iri:
            out_edge_dict = {
                "_label": self.DTP_CONFIG.get_ontology_uri('hasOperation'),
                "_targetIRI": operation_iri
            }
            out_edge_to_operation.append(out_edge_dict)

        query_dict = {
            "_classes": [self.DTP_CONFIG.get_ontology_uri('asPerformedConstruction')],
            "_domain": self.DTP_CONFIG.get_domain(),
            "_iri": constr_node_iri,
            "_visibility": 0,
            "_outE": [
                *out_edge_to_operation
            ]
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

        response = self.post_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('add_node'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info("DTP_API - NEW_CONSTRUCTION_IRI: " + constr_node_iri)
                return True
            else:
                logger_global.error("Creating new element failed. Response code: " + str(response.status_code))
                return False
        return True

    def create_kpi_zerodefectwork(self, kpi_node_iri, value, ref_quant, sampl_quant, inter_start_date, inter_end_date):

        if not validators.url(kpi_node_iri):
            raise Exception("Sorry, the IRI: " + kpi_node_iri + " is not a valid URL.")

        payload = json.dumps([
            {
                "_classes": [self.DTP_CONFIG.get_ontology_uri('kpiZeroDefectWork')],
                "_domain": self.DTP_CONFIG.get_kpi_domain(),
                "_iri": kpi_node_iri,
                "_visibility": 0,
                self.DTP_CONFIG.get_ontology_uri('kpiValue'): value,
                self.DTP_CONFIG.get_ontology_uri('kpiReferenceQuantity'): ref_quant,
                self.DTP_CONFIG.get_ontology_uri('kpiSampleQuantity'): sampl_quant,
                self.DTP_CONFIG.get_ontology_uri('kpiIntervalStartDate'): inter_start_date,
                self.DTP_CONFIG.get_ontology_uri('kpiIntervalEndDate'): inter_end_date,
            }
        ])

        response = self.post_guarded_request(payload=payload, url=self.DTP_CONFIG.get_api_url('add_node'))
        if not self.simulation_mode:
            if response.ok:
                if self.session_logger is not None:
                    self.session_logger.info("DTP_API - NEW_KPI_IRI: " + kpi_node_iri)
                return True
            else:
                logger_global.error("Creating new element failed. Response code: " + str(response.status_code))
                return False
        return True
