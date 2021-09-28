# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2021
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import models, fields


class Picking(models.Model):
    _inherit = "stock.picking"

    x_workorder_id = fields.Many2one(
        'telco.workorder',
        string="WorkOrder")
    
    crm_document_id = fields.Integer('CRM Document Id')
    
    def action_sync(self):
        return True