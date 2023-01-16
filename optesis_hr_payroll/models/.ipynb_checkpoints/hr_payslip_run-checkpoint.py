import time
from datetime import datetime, date, timedelta, time as t
from dateutil import relativedelta
from odoo.tools import float_compare, float_is_zero
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class HrPayslipRun(models.Model):
    _name = "hr.payslip.run"
    _inherit = ['hr.payslip.run', 'mail.thread', 'mail.activity.mixin']

    def unlink(self):
        for slip in self.slip_ids:#les fiches
            if slip.number:
                raise ValidationError(_('impossible de supprimer des bulletins avec une séquence!'))
        return super(HrPayslipRun, self).unlink()
    
    


    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('cancel', 'Annulé'),
         ('confirm', 'Confirmé'),
        ('validate', 'Validé'),
        ('done', 'Cloturé'),
        ('compta', 'Comptabilisé')
    ], string='Status', index=True, readonly=True, copy=False, default='draft', tracking = True)
    

    
        
    def draft_payslip_run(self):
        for slip in self.slip_ids:#les fiches
            if slip.state != 'draft':
                slip.action_payslip_draft()
        return self.write({'state': 'draft'})

    def close_payslip_run(self):
        for slip in self.slip_ids:#les fiches
            if slip.state != 'cancel':
                slip.action_payslip_cancel()
        return self.write({'state': 'cancel'})
    
    
     
    
    #def draft_payslip_run(self):
        #for slip in self.slip_ids:#les fiches
            #if slip.state != 'confirm':
                #slip.get_worked_day_lines
        #self.write({'state': 'draft'})

    #button confirmé
    def action_payslip_confirm(self):
        for slip in self.slip_ids:#les fiches
            if slip.state != 'confirm':
                slip.number = self.env['ir.sequence'].next_by_code('salary.slip')
                slip.action_payslip_confirm()#pour confirmer sur les fiches
        self.write({'state': 'confirm'})
        
      
    
    #button pour valider
    def validate_payslip(self):
        for slip in self.slip_ids:#les fiches
            if slip.state != 'validate':
                slip.action_payslip_validate()#pour valider sur les fiches
        self.write({'state': 'validate'})
        
     #button pour cloturer
    def cloture_payslip(self):
        for slip in self.slip_ids:#les fiches
            if slip.state != 'done':
                slip.action_payslip_done()#pour cloturer sur les fiches
        self.write({'state': 'done'})
        