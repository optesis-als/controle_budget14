# -*- coding: utf-8 -*-
from odoo import fields, models, _

#la sciété actuel 

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)
    
class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'
    
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)
    
class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'
    
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)
    
    

class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'
    
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)
    
    
class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)

    
class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'
    
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)



class HrSalaryCategoryMultiCompany(models.Model):
    """inherit model for removing required=True for company field """
    _inherit = 'hr.salary.rule.category'

    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)


       

class HrRuleInput(models.Model):
    _inherit = 'hr.rule.input'
    
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    company_id = fields.Many2one('res.company', 'Company', copy=False,
                                 default=lambda self: self.env.user.company_id)

