# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

{
    'name': 'X Vendor Bill',
    'version': '0.01',
    'category': 'Accounting',
    "author": "Kitcharoen Poolperm <kitcharoenp@gmail.com>",
    'summary': 'Vendor bill customize',
    'description': """
    """,
    'depends': ['account'],
    'data': [
        # Views
        'views/x_account_move_form_view.xml',
        'views/x_account_move_tree_view.xml',
        # Reports and Templates
    ],
    'installable': True,
    'application': True,
}
