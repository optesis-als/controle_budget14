# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    #fiche de paie
    slip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslips', readonly=True)
    payslip_count = fields.Integer(compute='_compute_payslip_count', string='Feuilles de paye')
    #nbre de fiche
    def _compute_payslip_count(self):
        for employee in self:
            employee.payslip_count = len(employee.slip_ids)

            
    number_of_days_work = fields.Float(string="Nombre de jours de travail",         related='company_id.number_of_days_work')
    number_of_hours_work = fields.Float(string="Nombre d'heures de travail", related='company_id.number_of_hours_work')