# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TelcoWorkorder(models.Model):
    _name = "telco.workorder"
    _description = "Telco Work Order"
    _order = "id desc"

    name = fields.Char(
        'Work Order',
        required=True)

    crm_id = fields.Integer('CRM Id')

    status = fields.Char(string='Status')
    sap_network = fields.Char(string='Sap Network')
    customer = fields.Char(string='Customer')

    service_ref1 = fields.Char(string='Service Ref.1')
    service_ref2 = fields.Char(string='Service Ref.2')
    noc_case_id = fields.Char(string='NOC Case Id')

    description = fields.Text('Description')
