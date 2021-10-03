# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2020
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    x_service_ref1 = fields.Char(string='Service Ref.1')
    x_service_ref2 = fields.Char(string='Service Ref.2')
    x_sap_network = fields.Char(string='Sap Network')
    x_description = fields.Text(string='Description')
