# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2021
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"


    x_plan_qty = fields.Integer('Plan')
    x_drum_no = fields.Char('Drum No.')
    x_mark1 = fields.Integer('Mark1')
    x_mark2 = fields.Integer('Mark2')