import time
from datetime import datetime, date, time as t
from dateutil import relativedelta
from odoo.tools.misc import format_date
from odoo.tools import float_compare, float_is_zero
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

#Element variable
class EmployeeBonus(models.Model):
    _name = 'hr.employee.bonus'
    _description = 'Employee Bonus'

   
    #regle salerial
    salary_rule_id = fields.Many2one('hr.salary.rule', string="Salary Rule", required=True)
    #employee
    employee_id = fields.Many2one('hr.employee', string='Employee')
    #montant
    amount = fields.Float(string='Amount', required=True)
    #date debut
    date_from = fields.Date(string='Date From',
                            default=time.strftime('%Y-%m-%d'), required=True)
    #date fin
    date_to = fields.Date(string='Date To',
                          default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
                          required=True)
    state = fields.Selection([('active', 'Active'),
                              ('expired', 'Expired'), ],
                             default='active', string="State", compute='get_status')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    
    contract_id = fields.Many2one('hr.contract', string='Contract')
    
    
    #l'etat est active si date d'aujourdhuit en compris entre la date from et date to 
    def get_status(self):
        current_datetime = datetime.now()
        for i in self:
            x = datetime.strptime(str(i.date_from), '%Y-%m-%d')
            y = datetime.strptime(str(i.date_to), '%Y-%m-%d')
            if x <= current_datetime <= y:
                i.state = 'active'
            else:
                i.state = 'expired'
                
    