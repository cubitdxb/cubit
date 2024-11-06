# -*- coding: utf-8 -*-

{
    'name': "Renewal Category",
    'version': '15.0.1.0.0',
    'summary': '1.Menu for Renewal Category'
               '2.Menu for Cisco'
               '3.presales person domain',
    'description': 'This module helps you to display the menu for renewal category',
    'category': 'sale',
    'author': 'Hilsha',
    'website': 'http://www.voxtronme.com',
    'company': 'Voxtron Solutions',
    'depends': ['base', 'sale','crm_lead_fields','vox_user_groups','vox_sales_team_access'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',

}
