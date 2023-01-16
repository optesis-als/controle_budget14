#-*- coding:utf-8 -*-
from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    #Lot de paie
    batch_id = fields.Many2one('hr.payslip.run', string="Payroll Batch")