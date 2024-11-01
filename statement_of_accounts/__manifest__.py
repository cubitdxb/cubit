{
    'name': 'Statement Of Accounts',
    'version': '17.0.2.2.2',
    'category': 'Accounting',

    'summary': """ Statement of Accounts.""",
    'description': """
                    Statement of Accounts (SOA)
                    """,
    'author': 'Cybobits Technology',
    'website': "https://www.cybobits.com",
    'company': 'Cybobits Technology',
    'depends': ['base', 'account',],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_partner_ledger.xml',
        'wizard/wizard_soa.xml',
        'report/report.xml',
        'report/report_soa.xml',
        'report/report_partner_ledger.xml',
    ],

    'license': 'LGPL-3',

    'installable': True,
    'auto_install': False,
    'application': True,
}
