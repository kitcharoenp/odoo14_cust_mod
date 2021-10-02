# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2021
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import models, fields
from odoo.modules.module import get_module_resource

import requests
import json
from urllib import parse


class Picking(models.Model):
    _inherit = "stock.picking"

    x_workorder_id = fields.Many2one(
        'telco.workorder',
        string="WorkOrder")
    
    x_crm_document_id = fields.Integer('CRM Document Id')
    x_crm_document_name = fields.Integer('CRM Document')
    

    def _get_crm_conn_params(self):
        json_path = get_module_resource('x_stock_picking', 'static/', 'config.json')
        with open(json_path) as f:
            data = json.load(f)

        # load config from json
        crm_param = data['zurmo']
        return crm_param

    def _request_session(self):
        data = self._get_crm_conn_params()

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
        
        headers = {
            'Accept': 'application/json',
            'ZURMO_SESSION_ID': authenticationData['sessionId'],
            'ZURMO_TOKEN': authenticationData['token'],
            'ZURMO_API_REQUEST_TYPE': 'REST'}

        session.headers.update(headers)
        return session


    def flat_key(self, layer):
        """ Example: flat_key(["1","2",3,4]) -> "1[2][3][4]" """
        if len(layer) == 1:
            return layer[0]
        else:
            _list = ["[{}]".format(k) for k in layer[1:]]
            return layer[0] + "".join(_list)

    def flat_dict(self, _dict):
        if not isinstance(_dict, dict):
            raise TypeError("argument must be a dict, not {}".format(type(_dict)))

        def __flat_dict(pre_layer, value):
            result = {}
            for k, v in value.items():
                layer = pre_layer[:]
                layer.append(k)
                if isinstance(v, dict):
                    result.update(__flat_dict(layer,v))
                else:
                    result[self.flat_key(layer)] = v
            return result
        return __flat_dict([], _dict)

    def get_api_endpoint(self, id:int = 0, module_name:str = 'materialsControl', action:str = 'read') -> str:
    
        if action == 'create':
            endpoint = '/app/index.php/'+module_name+'s/'+module_name+'/api/create/'
        elif action == 'create': 
            endpoint = '/app/index.php/'+module_name+'s/'+module_name+'/api/update/'+str(id)
        else:
            endpoint = '/app/index.php/'+module_name+'s/'+module_name+'/api/read/'+str(id)
            
        return endpoint


    def api_read_crm_workorder(self):
        # get session with auth data
        session = self._request_session()

        # get params from json file
        data = self._get_crm_conn_params()

        # get api read endpoint by id
        endpoint = self.get_api_endpoint(self.x_workorder_id.crm_id, module_name = 'workorder', action='read')

        _url = data['url'] + endpoint

        # make api request get data
        response = session.get(_url)

        # closing the connection
        response.close()

        workorder = json.loads(response.text)
        return workorder

    def action_sync(self):
        for picking in self:
            picking.update({
                'note': self.api_read_crm_workorder(),
            })
        return True