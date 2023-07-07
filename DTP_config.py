# -*- coding: utf-8 -*-`


#  Copyright (c) Centre Inria d'Université Côte d'Azur, University of Cambridge 2023.
#  Authors: Kacper Pluta <kacper.pluta@inria.fr>, Alwyn Mathew <am3156@cam.ac.uk>
#  This file cannot be used without a written permission from the author(s).

import getpass
import os
from base64 import b64encode
from datetime import datetime, timedelta

import requests
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

    def __get_dev_thingin_token(self):
        print("Authentication...")
        auth_url = 'https://api.thinginthefuture.bim2twin.eu/auth'
        user_id = input("Email: ")
        # known issue: some terminals are not capable of echo-free input
        # warning will be raised if password cant be hidden in terminal
        password = getpass.getpass("Password: ")
        b64_val = b64encode(f"{user_id}:{password}".encode())

        payload = {}
        headers = {
            'Authorization': f"Basic {b64_val.decode()}"
        }
        response = requests.request("GET", auth_url, headers=headers, data=payload)
        if response.status_code == 200:
            with open(os.path.join(os.path.dirname(__file__), 'thingin_token.txt'), 'w') as f:
                f.write(response.text.strip())
            return response.text.strip()
        else:
            raise Exception("Authentication failed!")

    def __read_token_file(self, token_path):
        token = ""
        f = open(token_path, "r")
        lines = f.readlines()

        for line in lines:
            token = token + line.rstrip(' \t\n\r')
        f.close()

        if len(token) == 0:
            print("Sorry, the dev token file seems to be empty.")
            token = self.__get_dev_thingin_token()

        return token

    def __check_token_expired(self):
        token_path = os.path.join(os.path.dirname(__file__), 'thingin_token.txt')
        if os.path.isfile(token_path):
            modified_time = datetime.fromtimestamp(os.path.getctime(token_path))
            return True if (datetime.now() - modified_time) > timedelta(hours=24) else False
        else:
            return True

    def __get_dev_token(self):
        if self.__check_token_expired():
            return self.__get_dev_thingin_token()
        else:
            token_path = os.path.join(os.path.dirname(__file__), 'thingin_token.txt')
            return self.__read_token_file(token_path)

    def __map_api_urls(self, uris):
        for uri in uris:
            self.api_uris[uri.attrib['function'].strip(' \t\n\r')] = uri.text.strip(' \t\n\r')

    def __map_ontology_uris(self, uris):
        assert uris, "Empty ontology URIs!"
        for key, uri in uris.items():
            self.ontology_uris[key.strip(' \t\n\r')] = uri.strip(' \t\n\r')

    def __init__(self, config_path):
        dtp_configs = yaml.safe_load(open(config_path))
        dtp_maps = yaml.safe_load(open("uri_mappings.yaml"))

        self.token = self.__get_dev_token()

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
