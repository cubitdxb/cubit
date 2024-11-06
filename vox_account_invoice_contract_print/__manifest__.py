# -*- coding: utf-8 -*-
##############################################################################
#
#    VOXTRON SOLUTIONS LLP.
#    Copyright (C) 2017-TODAY VOXTRON SOLUTIONS (<http://www.voxtronme.com>).
#    Author: Muhammed Aslam(<http://www.voxtronme.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Invoice / Contract Print',
    'version': '15.0.1.0.0',
    'summary': 'Customized Invoice / Contract print ',
    'description': 'This module helps you to take customized print format for invoices and contracts',
    'category': 'Accounting',
    'author': 'Muhammed Aslam',
    'website': 'http://www.voxtronme.com',
    'company': 'Voxtron Solutions',
    'depends': ['account','web','purchase_print', 'vox_invoice_global_discount'],
    'data': [
               # 'views/account_invoice_views.xml',
               'views/invoice_report.xml',
               'views/invoice_contract_report.xml',
               'views/account_report.xml',
               'views/proforma_invoice.xml',
             ],
    'css': [],
    'images': [],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}