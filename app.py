# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Simon Fang <sifang@cisco.com>"
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# Import Section
from flask import Flask, render_template, request
from dotenv import load_dotenv
import meraki
import os

# Load environment variables
load_dotenv()

# Global variables
app = Flask(__name__)

MERAKI_API_KEY = os.getenv('MERAKI_API_KEY')

# Initalize SDK
dashboard = meraki.DashboardAPI(
    api_key = MERAKI_API_KEY,
    suppress_logging=True
    )

# Template variables
organizations = []
networks = []
selected_organization = []

# Methods


# Routes

# Main Page
@app.route('/')
def main():
    global organizations
    organizations = dashboard.organizations.getOrganizations()
    return render_template('columnpage.html', organizations = organizations, networks = [], selected_organization = [])

# User submits their organization selection in first rail
@app.route('/select_organization', methods=['POST', 'GET'])
def select_organization():
    global organizations
    global selected_organization
    global networks

    if request.method == 'POST':
        form_data = request.form
        print(form_data)

        organization_id = form_data['organization_id']

        for organization in organizations:
            if organization_id == organization['id']:
                selected_organization = organization 

        networks = dashboard.organizations.getOrganizationNetworks(organization_id)
        print(networks)

    return render_template('columnpage.html', organizations = organizations, networks = networks, selected_organization = selected_organization)

# User submits their network selection in the second and third rail
@app.route('/select_networks', methods=['POST', 'GET'])
def select_networks():
    global organizations
    global selected_organization
    global networks

    if request.method == 'POST':
        form_data = request.form
        print(form_data)

        if 'network_id' in form_data:
            form_dict = dict(form_data.lists())
            network_ids = form_dict['network_id']

            unbound_networks = []
            failed_unbound_networks = []


            for network_id in network_ids:
                try:
                    response = dashboard.networks.unbindNetwork(network_id)
                    print(response)
                    unbound_networks.append(network_id)
                except Exception as e:
                    print(e)
                    failed_unbound_networks.append((network_id, e))

    return render_template('columnpage.html', organizations = organizations, networks = networks, selected_organization = selected_organization,
        unbound_networks=unbound_networks, failed_unbound_networks=failed_unbound_networks)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)