from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class Employee(models.Model):
    _inherit = "hr.employee"
    
    matricule = fields.Char(string='Matricule', copy=False, readonly=True, index=True, default=lambda self: _(''))
    
    @api.model
    def create(self, vals):
        if vals.get('matricule', _('Matricule')) == _('Matricule'):
            vals['matricule'] = self.env['ir.sequence'].next_by_code('hr.employee.seq') or _('Matricule')
        result = super(Employee, self).create(vals)
        return result
    
    
    