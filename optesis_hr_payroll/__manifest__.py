# -*- coding: utf-8 -*-
{
    'name': "optesis_hr_payroll",

    'version': '14.0.0',
    'summary': """Gérez vos dossiers de paie salariale""",
    'description': """""",
    'category': 'Human Resources',
    'author': 'Optesis SA',
    'maintainer': 'Optesis',
    'company': 'Optesis SA',
    'website': 'https://www.optesis.com',

    # any module necessary for this one to work correctly
    'depends': ['optesis_hr_contract'],

    
    # always loaded
    'data': [
        'security/hr_payroll_security.xml',
        'security/ir.model.access.csv',
        'data/hr_payroll_sequence.xml',
        'data/hr_payroll_category.xml',
        'data/hr_payroll_data.xml',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payroll_report.xml',
        'wizard/hr_payroll_contribution_register_report_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_contribution_register_templates.xml',
        'views/report_payslip_templates.xml',
        'views/report_payslip_details_templates.xml',
        'views/hr_payslip_inherit.xml',
        'views/hr_payslip_run.xml',
        'data/mail_template.xml',
        'views/menu_reports_payslip.xml',
        'views/res_config_inherit.xml',
        
        'data/sequence_inherit.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
