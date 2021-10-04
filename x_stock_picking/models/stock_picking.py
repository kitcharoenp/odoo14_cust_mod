# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2021
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models
from odoo.modules.module import get_module_resource

import requests
import json
from urllib import parse
from datetime import datetime


class Picking(models.Model):
    _inherit = "stock.picking"

    x_workorder_id = fields.Many2one(
        'telco.workorder',
        string="WorkOrder")
    
    x_crm_document_id = fields.Integer('CRM Document Id')
    x_crm_document_name = fields.Char('CRM Document')
    x_crm_document_status = fields.Char('CRM Status')
    

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

        # get params from json file
        data = self._get_crm_conn_params()
    
        if action == 'create':
            endpoint = '/app/index.php/'+module_name+'s/'+module_name+'/api/create/'
        elif action == 'update': 
            endpoint = '/app/index.php/'+module_name+'s/'+module_name+'/api/update/'+str(id)
        elif action == 'list':
            endpoint = '/app/index.php/'+module_name+'s/'+module_name+'/api/list/filter/'
        else:
            endpoint = '/app/index.php/'+module_name+'s/'+module_name+'/api/read/'+str(id)
            
        return data['url'] + endpoint

    def resolve_sapMovement_type(self, sap_network_prefix:str = 'WON', is_outbound:bool = 1):
        # check picking_type
        if self.picking_type_id.code == 'incoming':
            is_outbound = 0

        sap_movement_type = dict()
        sap_movement_type[1] = dict()
        sap_movement_type[0] = dict()
        sap_movement_type[1]['WON'] = 'Z81_REQ_for_ServiceOrder'
        sap_movement_type[1]['WOP'] = 'Z01_REQ_for_Project'
        sap_movement_type[1]['WOR'] = 'Z61_REQ_for_Maintenance_WorkOrder'

        sap_movement_type[0]['WON'] = 'Z82_RET_for_ServiceOrder'
        sap_movement_type[0]['WOP'] = 'Z02_RET_for_Project'
        sap_movement_type[0]['WOR'] = 'Z62_RET_for_Maintenance_WorkOrder'
        
        return sap_movement_type[is_outbound][sap_network_prefix]

    def crm_materials_control_payload_create_new(self):

        workorder = self.api_read_crm('workorder', self.x_workorder_id.crm_id)

        sap_network_prefix = workorder['data']['sapNetworkPrefix']

        # resolve `sap_movement_type` from `workorder`
        sap_movement_type = self.resolve_sapMovement_type(sap_network_prefix)

        _warehouses  = self.api_crm_list_by_field(
            module_name='warehouse', field='name', value='ODOO_SUB')

        if _warehouses['data']['totalCount'] > 0:
            warehouse = _warehouses['data']['items'][0]

        now = datetime.now()
        payload = {
            "data": {
                "name": 'New',
                'status' : {'value' : 'Initial'},

                "odooDocument": self.name,
                "odooDocumentId": self.id,
                "odooNote": str(self.note) + ' odoo_update : '+str(now),
                
                # resolve from sapNetworkPrefix and is_outbound
                'sapMovementType' : {'value' : sap_movement_type},
                #'explicitReadWriteModelPermissions': {'type': 1},

                # resolve from workorder
                'workorder' : {'id' : workorder['data']['id']},
                'owner' : {'id' : workorder['data']['supervisor']['id']},
                'supervisor' : {'id' : workorder['data']['supervisor']['id']},
                'recipient' : {'id' : workorder['data']['supervisor']['id']},
                'confirmedBy' : {'id' : workorder['data']['supervisor']['id']},
                "description": workorder['data']['company_B'] + workorder['data']['description'],
                    
                # resolve from Warehouse
                'warehouse' : {'id' : warehouse['id']},
                'storeKeeper' : {'id' : warehouse['storeKeeper']['id']},
                'warehouseController' : {'id' : warehouse['warehouseController']['id']},

                # resolve Contractor

                'checkedStatus' : {'value' : ''},
                'confirmedStatus' : {'value' : ''},
                'verifiedStatus' : {'value' : ''},
                'approvedStatus' : {'value' : ''},

                # TODO : mapping vendor field
            }
        }

        return payload

    def make_crm_payload_materials_control_update(self, payload:str = {}):

        now = datetime.now()

        if self.x_crm_document_id > 0:
            res = self.api_read_crm('materialsControl', self.x_crm_document_id)
            
            payload = {
                "data": {
                    'odooNote': ' odoo_update : '+str(now),
                }
            }
        return payload

    def api_read_crm(self, module_name:str = 'materialsControl', record_id:int = 1):
        
        endpoint = self.get_api_endpoint(record_id, module_name, action='read')

        # get session with auth data

        with self._request_session() as s:
        
            response = s.get(endpoint)

            json_res = json.loads(response.text)

            # closing the connection
            response.close()
    
            return json_res

    def api_update_crm(self, module_name:str = 'materialsControl', record_id:int = 1, payload:str = {}):
        
        endpoint = self.get_api_endpoint(record_id, module_name, action='update')

        with self._request_session() as s:

            # Encoded into a URL string
            url_str = parse.urlencode(self.flat_dict(payload))  
        
            response = s.put(endpoint, data=url_str)

            json_res = json.loads(response.text)

             # closing the connection
            response.close()
            
            return json_res

    def api_crm_list_by_field(self, module_name:str='materialsControl', field:str='name', value:str='') -> str:

        endpoint = self.get_api_endpoint(module_name=module_name, action='list')

        payload = {
            "search": {
                field: value,
            }
        }
        
        with self._request_session() as s:

            # Encoded into a URL string
            payload_urlstr = parse.urlencode(self.flat_dict(payload))  
        
            response = s.get(endpoint+payload_urlstr)

            json_res = json.loads(response.text)

             # closing the connection
            response.close()
            
            return json_res

    def search_materialsControl_items_by_code_and_smaterialsControl_id(self, module_name:str='billofMaterial', field:str='code', value:str='') -> str:

        endpoint = self.get_api_endpoint(module_name=module_name, action='list')

        payload = {
            "search": {
                field: value,
                'materialsControl' : {'id': self.x_crm_document_id}
            }
        }
        
        with self._request_session() as s:

            # Encoded into a URL string
            payload_urlstr = parse.urlencode(self.flat_dict(payload))  
        
            response = s.get(endpoint+payload_urlstr)

            json_res = json.loads(response.text)

             # closing the connection
            response.close()
            
            return json_res

    def api_create_crm(self, payload:str, module_name:str = 'materialsControl'):

        endpoint = self.get_api_endpoint(module_name=module_name, action='create')

        with self._request_session() as s:

            # Encoded into a URL string
            payload_urlstr = parse.urlencode(self.flat_dict(payload))  
        
            response = s.put(endpoint, data=payload_urlstr)

            json_res = json.loads(response.text)

            # closing the connection
            response.close()
    
            return json_res

    def create_new_materials_control(self, picking):
        # create a new crm materialsControl record
        payload = self.crm_materials_control_payload_create_new()
        crm_materialsControl = self.api_create_crm(payload, 'materialsControl')

        # update odoo record
        picking.update({
            'x_crm_document_id': crm_materialsControl['data']['id'],
            'x_crm_document_name': crm_materialsControl['data']['name'],
            'x_crm_document_status': crm_materialsControl['data']['status']['value'],
        })

    def action_sync(self):

        for picking in self:

            # 1. create a new crm materials_control record if x_crm_document_id is null
            if not (self.x_crm_document_id > 0):
                self.create_new_materials_control(picking)
            

            if self.x_crm_document_id > 0:

                # update crm materialsControl record
                payload = self.make_crm_payload_materials_control_update()
                crm_materialsControl = self.api_update_crm('materialsControl', self.x_crm_document_id, payload)

                # update x_crm_document_status
                picking.update({
                    'x_crm_document_status': crm_materialsControl['data']['status']['value'],
                })
                
                # create / update materialsControl items
                for m in picking.move_lines:
                    now = datetime.now()
                    code = m.product_id.default_code

                    # 1. search crm productTemplate by `code`
                    _product_templates  = self.api_crm_list_by_field(module_name='productTemplate', field='code', value=code)
                    
                    # 2. search crm materialsControl item by `code` and materialsControl `id`
                    materialsControl_items = self.search_materialsControl_items_by_code_and_smaterialsControl_id(value=code)
                    
                    # 4. if code is exist update else create
                    if materialsControl_items['data']['totalCount'] > 0:
                        payload = {
                            "data": {
                                'plannedQuantity': m.x_plan_qty,
                                'identitynumber':  m.x_drum_no + ' [ ' + str(m.x_mark1) + ' / ' + str(m.x_mark2) +' ]',
                                #'mark1': m.x_mark1,
                                #'mark2': m.x_mark2,
                                'description': ' odoo_update : ' + str(now),
                                'owner' : {'id' : crm_materialsControl['data']['owner']['id']},
                            }  
                        }

                        # 4.1 update
                        materialsControl_item_id = materialsControl_items['data']['items'][0]['id']

                        # update materialsControl_item by id
                        crm_materialsControl_item = self.api_update_crm('billofMaterial', materialsControl_item_id, payload)
                    
                    else:
                        # 4.2 create
                        if _product_templates['data']['totalCount'] > 0:
                            product_template = _product_templates['data']['items'][0]

                            payload = {
                                "data": { 
                                    'materialitem': {'id': product_template['id']},
                                    'name': product_template['name'],
                                    'code': product_template['code'],
                                    'unit': product_template['unit'],
                                    'priceperunit': {
                                        'value' : product_template['cost']['value'],
                                        'currency' : {'id' : 2}
                                    },

                                    'materialsControl': {'id': self.x_crm_document_id},

                                    'plannedQuantity': m.x_plan_qty,
                                    'identitynumber':  m.x_drum_no + ' [ ' + str(m.x_mark1) + ' / ' + str(m.x_mark2) +' ]',
                                    #'mark1': m.x_mark1,
                                    #'mark2': m.x_mark2,

                                    'description': ' odoo_update : '+str(now) + product_template['name'],
                                    # set owner from materialsControl owner
                                    'owner' : {'id' : crm_materialsControl['data']['owner']['id']},
                                }
                            }

                            crm_materialsControl_item = self.api_create_crm(payload, module_name='billofMaterial')

        return True 