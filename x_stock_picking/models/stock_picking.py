# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2021
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import models, fields
from odoo.modules.module import get_module_resource

import requests
import json


class Picking(models.Model):
    _inherit = "stock.picking"

    x_workorder_id = fields.Many2one(
        'telco.workorder',
        string="WorkOrder")
    
    x_crm_document_id = fields.Integer('CRM Document Id')
    x_crm_document_name = fields.Integer('CRM Document')
    

    def _set_crm_conn_params(self):
        json_path = get_module_resource('x_stock_picking', 'static/', 'config.json')
        with open(json_path) as f:
            data = json.load(f)

        # load config from json
        crm_param = data['zurmo']
        return crm_param

    def _request_session(self):
        data = self._set_crm_conn_params()

        login_header={
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'ZURMO_AUTH_USERNAME' : data['username'], 
            'ZURMO_AUTH_PASSWORD' : data['password'],
            'ZURMO_API_REQUEST_TYPE' : 'REST'
        }

        # all cookies received will be stored in the session object
        session=requests.Session()
        session.headers.update(login_header)

        # Get  Authentication `sessionId/token`
        login_url = data['url']+'/app/index.php/zurmo/api/login'

        respose_login = session.post(login_url)
        auth_respose = json.loads(respose_login.text)
        authenticationData=auth_respose['data']

        # closing the connection
        respose_login.close()

        return authenticationData['sessionId'], authenticationData['token']


    def action_sync(self):
        for picking in self:
            picking.update({
                'note': self._request_session(),
            })
        return True