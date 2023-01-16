# -*- coding: utf-8 -*-
{
    'name': "optesis_hr_payroll_bonus",

  
    'version': '14.0.0',
    'summary': """Gérez les élements variables sur vos fiches de Paie""",
    'description': """""",
    'category': 'Human Resources',
    'author': 'Optesis',
    'maintainer': 'Optesis',
    'company': 'Optesis SA',
    'website': 'https://www.optesis.com',

    # any module necessary for this one to work correctly
     'depends': [
        'optesis_hr_payroll',
        'optesis_hr_contract',
    ],

    # always loaded
    'data': [
        'views/employee_bonus_view.xml',
        'security/security_societe.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
