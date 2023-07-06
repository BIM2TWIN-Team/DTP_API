# -*- coding: utf-8 -*-`


#  Copyright (c) Centre Inria d'Université Côte d'Azur, University of Cambridge 2023.
#  Authors: Kacper Pluta <kacper.pluta@inria.fr>, Alwyn Mathew <am3156@cam.ac.uk>
#  This file cannot be used without a written permission from the author(s).

import os

import validators
import yaml


class DTPConfig:
    """
    The class is used to map DTP configuration from an XML file.

    Attributes
    ----------
    token : str
        the developer token
    dtp_domain : str
        a domain URL
    api_uris : dictionary
        a map of the API uris
    ontology_uris : dictionary
        a map of the ontology uris        

    Methods
    -------
    get_api_uri(api_type, ID)
        if the type is a valid type from the XML configuration, then it returns the link,
        if the ID is provided, then the returned link will contain it
    get_ontology_uri(ontology_type)
        if the type is a valid type from the XML configuration, then it returns
        the corresponding ontology URI
    get_token()
        return the developer token
    get_kpi_domain()
        returns the KPI domain
    get_domain()
        returns the DTP domain
    """

    def __read_dev_token(self, input_dev_token_file):
        if not os.path.exists(input_dev_token_file):
            raise Exception("Sorry, the dev token file does not exist.")

        token = ''

        f = open(input_dev_token_file, "r")
        lines = f.readlines()

        for line in lines:
            token = token + line.rstrip(' \t\n\r')
        f.close()

        if len(token) == 0:
            raise Exception("Sorry, the dev token file seems to be empty.")

        return token

    def __map_api_urls(self, urls):
        assert urls, "Empty API URLs!"
        for key, uri in urls.items():
            self.api_uris[key.strip(' \t\n\r')] = uri.strip(' \t\n\r')

    def __map_ontology_uris(self, uris):
        assert uris, "Empty ontology URIs!"
        for key, uri in uris.items():
            self.ontology_uris[key.strip(' \t\n\r')] = uri.strip(' \t\n\r')

    def __init__(self, config_path):
        dtp_configs = yaml.safe_load(open(config_path))
        dtp_maps = yaml.safe_load(open("uri_mappings.yaml"))

        token_path = dtp_configs["DEV_TOKEN"].strip(' \t\n\r')
        self.token = self.__read_dev_token(token_path)

        self.dtp_domain = dtp_configs["DTP_DOMAIN"].strip(' \t\n\r')
        if not validators.url(self.dtp_domain):
            raise Exception("Sorry, the DTP domain URL is not a valid URL.")

        if self.dtp_domain[-1] != '/':
            self.dtp_domain = self.dtp_domain + '/'

        self.kpi_domain = dtp_configs["KPI_DOMAIN"].strip(' \t\n\r')
        if not validators.url(self.kpi_domain):
            raise Exception("Sorry, the DTP domain URL is not a valid URL.")

        if self.kpi_domain[-1] != '/':
            self.kpi_domain = self.kpi_domain + '/'

        self.log_dir = dtp_configs["LOG_DIR"].strip(' \t\n\r')
        assert self.log_dir != "/path/to/log/dir", "Please set LOG_DIR in DTP_config.yaml"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.api_uris = {}
        urls = dtp_maps["API_URLS"]
        if urls is not None:
            self.__map_api_urls(urls)

        self.ontology_uris = {}
        uris = dtp_maps["ONTOLOGY_URIS"]
        if uris is not None:
            self.__map_ontology_uris(uris)

    def get_api_url(self, api_type, idx=None):
        assert api_type in self.api_uris.keys(), f"APU URL {api_type} not found!"
        if len(idx.strip(' \t\n\r')) == 0:
            return self.api_uris[api_type]
        else:
            return self.api_uris[api_type].replace('_ID_', idx)

    def get_ontology_uri(self, ontology_type):
        assert ontology_type in self.ontology_uris.keys(), f"Ontology {ontology_type} not found!"
        return self.ontology_uris[ontology_type]

    def get_token(self):
        return self.token

    def get_kpi_domain(self):
        return self.kpi_domain

    def get_domain(self):
        return self.dtp_domain

    def get_log_path(self):
        return self.log_dir


# Below code snippet for testing only
if __name__ == "__main__":
    dtp_config = DTPConfig("./DTP_config.yaml")
    print('Token:', dtp_config.get_token())
    print('URI:', dtp_config.get_ontology_uri('isAsDesigned'))
