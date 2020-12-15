# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    x_account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account')

    x_service_ref1 = fields.Char(string='Service Ref.1')
    x_service_ref2 = fields.Char(string='Service Ref.2')
    x_sap_network = fields.Char(string='Sap Network')

    x_requestor_id = fields.Many2one(
        'hr.employee',
        string="Requestor")
    x_manager_id = fields.Many2one(
        'hr.employee',
        string="Manager")
    x_verified_id = fields.Many2one(
        'hr.employee',
        string="Verified By")
    x_description = fields.Text(string='Description')

    @api.depends('name', 'partner_ref')
    def name_get(self):
        result = super(PurchaseOrder, self).name_get()
        result = []
        for po in self:
            name = po.name
            result.append((po.id, name))
        return result

    # update order_line taxes with default purchase vendor taxs
    def action_default_purchase_line_taxs(self):
        for order in self:
            order.order_line.update({
                'taxes_id': order.partner_id.x_purchase_taxes_id})
