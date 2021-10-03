# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2021
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License
{
    'name': 'X Stock Picking',
    'description': "",
    'category': 'Inventory/Inventory',
    "author": "Kitcharoen Poolperm <kitcharoenp@gmail.com>",
    'depends': ['stock', 'telco_workoder'],

    'data': [
        # Views
        'views/x_stock_picking_form_view.xml',
        'views/x_stock_picking_tree_view.xml',
    ],

    'installable': True,
}