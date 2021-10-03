# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2021
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'Telco Workorder',
    'version': '0.01',
    'license': 'AGPL-3',
    "author": "Kitcharoen Poolperm <kitcharoenp@gmail.com>",
    'description': """
        Work Order for Telecommunication""",
    'depends': ['base_setup'],
    'data': [
        # Security
        'security/telco_workorder_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        # Acion
        'actions/telco_workorder_act_window.xml',

        # Views
        'views/telco_workorder_menu_view.xml',
        'views/telco_workorder_form_view.xml',
        'views/telco_workorder_tree_view.xml',
        # Search
        # Reports and Templates
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
