# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'X Purchase Order',
    'version': '0.01',
    'category': 'Purchases',
    "author": "Kitcharoen Poolperm <kitcharoenp@gmail.com>",
    'summary': 'Purchase Orders customize',
    'description': """
        1. payment summary report
        2. default purchase tax button for purchase order
    """,
    'depends': ['purchase',
                'project',
                'x_account_move'],
    'data': [
        # Security
        'security/x_purchase_security_groups.xml',
        'security/ir.model.access.csv',
        'security/x_purchase_security_rules.xml',
        # Data
        'data/x_purchase_sequence_data.xml',
        # Views
        'views/x_purchase_order_tree_view.xml',
        'views/x_purchase_order_form_view.xml',
        'views/x_purchase_rescompany_form_view.xml',
        'views/x_purchase_res_partner_form_view.xml',
        # Search
        'views/x_purchase_order_search_view.xml',
        # Reports and Templates
        'reports/x_purchase_report.xml',
        'reports/templates/payment_report_by_po_templates.xml',
        'reports/templates/report_material_balance.xml',
        'reports/templates/material_balance_templates.xml',
    ],
    'installable': True,
    'application': True,
}
