# -*- coding: utf-8 -*-`


#  Copyright (c) Centre Inria d'Université Côte d'Azur, University of Cambridge 2023.
#  Authors: Kacper Pluta <kacper.pluta@inria.fr>, Alwyn Mathew <am3156@cam.ac.uk>
#  This file cannot be used without a written permission from the author(s).

import getpass
import os
import xml.etree.ElementTree as ET
from base64 import b64encode
from datetime import datetime, timedelta

import requests
import validators


class DTPConfig:
    """
    The class is used to map DTP configuration from an XML file.

    Attributes
    ----------
    version : str
        configuration file version
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
    get_api_uri(api_type, ID = ' ')
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
    get_version()
        returns the config. file version
    get_object_types()
        returns list, str, object types
    get_object_type_classes()
        returns list, str, object type classes
    get_object_type_conversion_map()
        returns dictionary, str, object type maps
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
        for uri in uris:
            self.ontology_uris[uri.attrib['function'].strip(' \t\n\r')] = uri.text.strip(' \t\n\r')

    def __map_object_types(self, objet_types):
        for obj_type in objet_types:
            if not obj_type.text.strip(' \t\n\r') in self.objet_types:
                self.objet_types.append(obj_type.text.strip())
            if not obj_type.attrib['field'].strip(' \t\n\r') in self.objet_type_classes:
                self.objet_type_classes.append(obj_type.attrib['field'].strip(' \t\n\r'))

    def __map_object_type_conversions(self, objet_type_map):
        for type_map in objet_type_map:
            self.objet_type_maps[type_map.attrib['from'].strip(' \t\n\r')] = type_map.attrib['to'].strip(' \t\n\r')

    def __init__(self, xml_path):
        config = ET.parse(xml_path).getroot()

        self.version = config.find('VERSION').text.strip(' \t\n\r')

        self.token = self.__get_dev_token()

        self.dtp_domain = config.find('DTP_DOMAIN').text.strip(' \t\n\r')
        if not validators.url(self.dtp_domain):
            raise Exception("Sorry, the DTP domain URL is not a valid URL.")

        if self.dtp_domain[-1] != '/':
            self.dtp_domain = self.dtp_domain + '/'

        self.kpi_domain = config.find('KPI_DOMAIN').text.strip(' \t\n\r')
        if not validators.url(self.kpi_domain):
            raise Exception("Sorry, the DTP domain URL is not a valid URL.")

        if self.kpi_domain[-1] != '/':
            self.kpi_domain = self.kpi_domain + '/'

        self.log_dir = config.find('LOG_DIR').text.strip(' \t\n\r')
        assert self.log_dir != "/path/to/log/dir", "Please set LOG_DIR in DTP_config.xml"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.api_uris = {}
        uris = config.find('API_URLS')
        if not uris is None:
            self.__map_api_urls(uris)

        self.ontology_uris = {}
        uris = config.find('ONTOLOGY_URIS')
        if not uris is None:
            self.__map_ontology_uris(uris)

        self.objet_type_classes = []
        self.objet_types = []
        objet_types = config.find('OBJECT_TYPES')
        if not objet_types is None:
            self.__map_object_types(objet_types)

        self.objet_type_maps = {}
        objet_type_map = config.find('OBJECT_TYPE_CONVERSIONS')
        if not objet_type_map is None:
            self.__map_object_type_conversions(objet_type_map)

    def get_api_url(self, api_type, id=' '):
        if len(id.strip(' \t\n\r')) == 0:
            return self.api_uris[api_type]
        else:
            return self.api_uris[api_type].replace('_ID_', id)

    def get_ontology_uri(self, ontology_type):
        return self.ontology_uris[ontology_type]

    def get_token(self):
        return self.token

    def get_kpi_domain(self):
        return self.kpi_domain

    def get_domain(self):
        return self.dtp_domain

    def get_version(self):
        return self.version

    def get_log_path(self):
        return self.log_dir

    def get_object_types(self):
        return self.objet_types

    def get_object_type_classes(self):
        return self.objet_type_classes

    def get_object_type_conversion_map(self):
        return self.objet_type_maps
