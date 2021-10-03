# pylint: disable=no-member
# -*- coding: utf-8 -*-

from odoo import fields, models


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
    cont_stock_picking_incoming = fields.Integer(
        compute="_compute_count_all", 
        string='Incoming Count')
    cont_stock_picking_outgoing = fields.Integer(
        compute="_compute_count_all", 
        string='Outgoing Count')


    def _compute_count_all(self):
        stock_picking = self.env['stock.picking']

        for record in self:
            record.cont_stock_picking_incoming = stock_picking.search_count([
                    ('x_workorder_id', '=', record.id), 
                    ('picking_type_id', '=', 1), #TODO: fix picking_type_id 1,2
                    ('partner_id', '=', self.env.user.partner_id.id),
                ])

            record.cont_stock_picking_outgoing = stock_picking.search_count([
                    ('x_workorder_id', '=', record.id), 
                    ('picking_type_id', '=', 2),
                    ('partner_id', '=', self.env.user.partner_id.id),
                ])

    def open_stock_picking_incoming(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receipts',
            'view_mode': 'tree,kanban,form',
            'res_model': 'stock.picking',
            'domain': [
                ('x_workorder_id', '=', self.id), 
                ('picking_type_id', '=', 1),
            ],
            'context': {
                'default_x_workorder_id': self.id,  
                'default_picking_type_id': 1,
                'default_partner_id': self.env.user.partner_id.id,
            }
        }

    def open_stock_picking_outgoing(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery',
            'view_mode': 'tree,kanban,form',
            'res_model': 'stock.picking',
            'domain': [
                ('x_workorder_id', '=', self.id),
                ('picking_type_id', '=', 2),
            ],
            'context': {
                'default_x_workorder_id': self.id,
                'default_picking_type_id': 2,
                'default_partner_id': self.env.user.partner_id.id,
            }
        }