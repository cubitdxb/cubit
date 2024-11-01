# -*- coding: utf-8 -*-
##########################################################################################
#
#    Voxtron solutions.
#    Copyright (C) 2018-TODAY Voxtron  Solutions (<https://www.voxtronme.com/>).
#
##########################################################################################
{
    'name': "Voxtron Geo Location",
    'version': '15.0',
    'category': 'industries',
    'currency': 'EUR',
    'maintainer': 'Voxtron solutions',
    'website': "https://www.voxtronme.com/",
    'license': 'OPL-1',
    'author': 'Jishnu K',
    'live_test_url': 'https://youtu.be/7S05EFje2mI',
    'summary': 'Track Employee location',
    # 'images': ['static/images/main_screenshot.png'],
    'depends': ['hr'],
    'external_dependencies': {'python': ['geopy']},
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/location_cron.xml',
        'views/res_config.xml',
        'views/hr_employee.xml',
        'views/employee_location_log.xml',
    ],
    'assets': {

    },
    'installable': True,
    'application': True,
}
