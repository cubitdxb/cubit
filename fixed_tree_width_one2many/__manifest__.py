# -*- coding: utf-8 -*-
{
    'name': "Fixed column width in one2many tree",

    'summary': """
        Fixed column width in one2many tree
        """,

    'description': """
        Fixed column width in one2many tree
    """,

    'author': "Hilsha",
    'website': "http://www.yourcompany.com",

    'version': '15.0.0.1',

      'license': 'LGPL-3',

    'category': 'App/',
    # 'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [

    ],

    'assets': {
        'web.assets_backend': [
            'fixed_tree_width_one2many/static/src/js/custom_width_tree.js',
            # 'fixed_tree_width_one2many/static/src/scss/main.scss',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
