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
    'name': 'Payment Allocation',
    'version': '15.0.1.0.0',
    'summary': 'Payment allocation for invoices and vendor bills',
    'description': 'This module helps you to set partial/full payment of invoices/vendor bills',
    'category': 'Accounting',
    'author': 'Muhammed Aslam',
    'website': 'http://www.voxtronme.com',
    'company': 'Voxtron Solutions',
    'depends': ['account', 'purchase', 'vox_vendor_bill'],
    'data': [
             'security/ir.model.access.csv',
             'views/account_payment_view.xml',
             ],
    'css': [],
    'images': [],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
