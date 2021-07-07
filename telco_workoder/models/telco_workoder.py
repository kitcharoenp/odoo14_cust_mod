# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TelcoWorkorder(models.Model):
    _name = "telco.workorder"
    _description = "Telco Work Order"
    _order = "id desc"

    name = fields.Char(
        'Work Order',
        required=True,
        states={
            'approved': [('readonly', True)],
            'rejected': [('readonly', True)]
            })

    state = fields.Selection([
        ('initial', 'Initial'),
        ('pending_checks', 'Pending Checks'),
        ('pending_confirmation', 'Pending Confirmation'),
        ('pending_verification', 'Pending Verification'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string='Status',
        default='pending',
        copy=False, readonly=True)

    sap_network = fields.Char(string='Sap Network')
    customer = fields.Char(string='Customer')

    service_ref1 = fields.Char(string='Service Ref.1')
    service_ref2 = fields.Char(string='Service Ref.2')
    noc_case_id = fields.Char(string='NOC Case Id')

    description = fields.Text('Description')
