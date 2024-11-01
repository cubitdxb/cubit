# -*- coding: utf-8 -*-
##########################################################################################
#
#    Voxtron solutions.
#    Copyright (C) 2018-TODAY Voxtron  Solutions (<https://www.voxtronme.com/>).
#
##########################################################################################
{
    'name': "Gross/Profit Amount view",
    'version': '15.0',
    'category': 'industries',
    'currency': 'EUR',
    'maintainer': 'Voxtron solutions',
    'website': "https://www.voxtronme.com/",
    'license': 'OPL-1',
    'author': 'Jishnu K',
    'live_test_url': 'https://youtu.be/7S05EFje2mI',
    'summary': 'Gross/Profit amount view in odoo sale order',
    'depends': ['sale', 'vox_task_template', 'vox_sale_fields'],
    'external_dependencies': {},
    'data': [
        # 'security/security.xml',
        'views/sale_order_list_inherit.xml'
    ],
    'assets': {

    },
    'installable': True,
    'application': True,
}
