from datetime import datetime, date, time as t
from odoo import models, fields, api, tools, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from pytz import timezone
from dateutil.relativedelta import relativedelta
#add babel import by mpb
import babel.dates
import logging
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _name = "hr.payslip"
    _inherit = ['hr.payslip', 'mail.thread', 'mail.activity.mixin']
    
    
    
    
    def unlink(self):
        if any(self.filtered(lambda payslip: payslip.number)):
            raise UserError(_('impossible de supprimer un bulletin avec une séquence!'))
        return super(HrPayslip, self).unlink()
    
    
    number = fields.Char(string='Reference', readonly=True, default=False)
    

    def compute_sheet(self):
        for payslip in self:
            
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines})
        return True

    
   
    #une mention brouillon quand le bulletin est à l'état brouillon                  
    number_draft = fields.Char(readonly=True, copy=False,  compute="_get_number")
    
    @api.depends('state')
    def _get_number(self):
        for rec in self: 
            if (rec.state == 'draft'):
                rec.number_draft = "En brouillon"
            else:
                rec.number_draft = False
    
    #un filter sur le champs line_ids
    calcul_salary_rule = fields.One2many('hr.payslip.line',
        compute='_compute_calcul_salary_rule', string='Calcul de salaire')
    
    
    def _compute_calcul_salary_rule(self):
        for payslip in self:
            payslip.calcul_salary_rule = payslip.mapped('line_ids').filtered(lambda line: line.appears_on_payslip)
            
    number_of_days_work = fields.Float(string="Nombre de jours de travail",  related='employee_id.number_of_days_work')
    number_of_hours_work = fields.Float(string="Nombre d'heures de travail",  related='employee_id.number_of_hours_work')
    


    
    def action_payslip_confirm(self):
        for payslip in self:
            payslip.number = self.env['ir.sequence'].next_by_code('salary.slip')
            return payslip.write({'state': 'confirm'}) 
    
    def action_payslip_done(self):
        for payslip in self:
            self.compute_sheet()
            return payslip.write({'state': 'done'}) 
    
   
    def action_payslip_validate(self):
        for payslip in self:
            #if not payslip.number:
                #payslip.compute_sheet() #appel à la fonction compute_sheet
            #contract_ids = payslip.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            #for line in payslip.line_ids:
                #if line.code == "C1060":
                    #self.env['hr.contract'].reinit(contract_ids)
                    #break

            return payslip.write({'state': 'validate'}) 
        
        
        
        
        
   
    #def action_payslip_cloture(self):
        #for payslip in self:
        
            #return payslip.write({'state': 'done'}) 

    def action_payslip_draft(self):
        return self.write({'state': 'draft'})

    

    def action_payslip_cancel(self):
        # if self.filtered(lambda slip: slip.state == 'done'):
        #     raise UserError(_("Cannot cancel a payslip that is done."))
        return self.write({'state': 'cancel'})
        
        
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('cancel', 'Annulé'),
        ('confirm', 'Confirmé'),
        ('validate', 'Validé'),
        ('done', 'clôturé'),
        ('compta', 'Comptabilisé'),
    ], tracking = True)  
    
    
    #on fixe le nombre d'heures et jours travaillés de la fiche par les champs récupérés à partir de la configuration et ulisiser sur la fiche
    number_of_days_work = fields.Float(string="Nombre de jours de travail",  related='employee_id.number_of_days_work')
    number_of_hours_work = fields.Float(string="Nombre d'heures de travail", related='employee_id.number_of_hours_work')
    
    
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), t.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), t.max)

            # compute leave days
            leaves = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': holiday.holiday_status_id.name or 'GLOBAL',
                    'number_of_days': self.number_of_days_display,
                    'number_of_hours': self.number_of_hours_display,
                    'contract_id': contract.id,
                })
                current_leave_struct['number_of_hours'] += hours
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(day, t.min)),
                    tz.localize(datetime.combine(day, t.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    current_leave_struct['number_of_days'] += hours / work_hours

            # compute worked days
            work_data = contract.employee_id._get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
            work_nber = contract.employee_id
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_nber['number_of_days_work'],
                'number_of_hours':  work_nber['number_of_hours_work'],
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res
    
    @api.model
    def create(self, vals):
        res = super(HrPayslip, self).create(vals)
        if not res.credit_note:
            cr = self._cr
            if res.contract_id.state == 'open':
                query = """SELECT date_from, date_to FROM "hr_payslip" WHERE employee_id = %s AND state = 'done'"""
                cr.execute(query, ([res.employee_id.id]))
                date_from_to = cr.fetchall()
                for items in date_from_to:
                    if res.date_from == items[0] and res.date_to == items[1]:
                        raise ValidationError(_("You cannot create payslip for the same period"))
                    else:
                        if not (items[1] <= res.date_from >= items[0] or items[0] >= res.date_to <= items[1]):
                            raise ValidationError(_("You cannot create payslip for the same period"))
            else:
                raise ValidationError(_("Vous ne pouvez pas créer une fiche de paie avec un contrat non ouvert! "))

        return res
    
    
    
    
    
   

                
   