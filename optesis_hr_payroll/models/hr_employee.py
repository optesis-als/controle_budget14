# -*- coding:utf-8 -*-

from odoo import api, fields, models



class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'
    
    number_of_days_work = fields.Float(string="Nombre de jours de travail",  compute='_compute_number_of_days_work')
    number_of_hours_work = fields.Float(string="Nombre d'heures de travail",compute='_compute_number_of_hours_work')
    
    @api.depends('payslip_count')
    def _compute_number_of_days_work(self):
        for payslip in self:
            payslip.number_of_days_work = self.env['ir.config_parameter'].sudo().get_param('optesis_hr_payroll.number_of_days_work') or False
    
            
    @api.depends('payslip_count')        
    def _compute_number_of_hours_work(self):
        for payslip in self:
            payslip.number_of_hours_work = self.env['ir.config_parameter'].sudo().get_param('optesis_hr_payroll.number_of_hours_work') or False
    

    #fiche de paie
    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Feuilles de paye')
    #nbre de fiche
    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)

            
    