# -*- coding: utf-8 -*-
{
   'name': 'Odoo 14 HR Payroll Accounting',
    'category': 'Generic Modules/Human Resources',
    'author': 'Optesis',
    'version': '14.0.0',
    'sequence': 1,
    'license': 'LGPL-3',
    'website': '',
   
    'summary': 'Generic Payroll system Integrated with Accounting',
    'description': """Generic Payroll system Integrated with Accounting.""",
    'depends': [
        'optesis_hr_payroll','account','account_accountant'],
    'data': [
        'views/hr_payroll_account_views.xml',
        'views/hr_payslip_run.xml',
        'views/account_move_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
