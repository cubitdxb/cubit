# -*- coding: utf-8 -*-
{
    'name': "Exception Details",

    'summary': """
        Exception Details""",

    'description': """
       Exception Details
    """,

    'author': "Jishnu K",
    'website': "http://www.yourcompany.com",
    'category': 'Technical',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/exception_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'license': 'LGPL-3',
}
