import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class HrPayslipInheritTrimf(models.Model):
    _inherit = 'hr.payslip'
    
    trimf_recalcule_cumul = fields.Float(string="brut current", compute="_get_trimf_recalcule_cumul")
    
   
    api.depends('employee_id')
    def _get_trimf_recalcule_cumul(self):
        for payslip in self:
            payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], limit=12)
            if line.date_from.year == payslip.date_from.year:
                cumul_trimf_recal = 0.0
                for line in payslip_ids:
                    cumul_trimf_recal += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == "C7520")# trimf cumul
                    payslip.trimf_recalcule_cumul = cumul_trimf_recal
                
                
    def get_brut_annual(self):
        self.ensure_one()
        for payslip in self:
            cumul_brut = 0.0
            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id), ('year', '=', payslip.date_from.year)], limit=11):
                if line.date_from.year == payslip.date_from.year:
                    cumul_brut += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == "C4500")#BRUT Imposable
            return cumul_brut+self.brut_of_current_payslip

   
    def get_annual_trimf(self):
        brut_impo_annual = self.get_brut_annual()
        result = 0.0
        if brut_impo_annual <= 599999:
            result = self.employee_id.trimf*900
        else:
            if brut_impo_annual >= 600000 and brut_impo_annual < 999996:
                result = self.employee_id.trimf*3600
            else:
                if brut_impo_annual >= 1000000 and brut_impo_annual < 1999999:
                    result = self.employee_id.trimf*4800
                else:
                    if  brut_impo_annual >= 2000000  and brut_impo_annual <  6999999:
                        result = self.employee_id.trimf*12000
                    else:
                        if brut_impo_annual >= 7000000  and brut_impo_annual <  11999999:
                            result = self.employee_id.trimf*18000
                        else:
                            result = self.employee_id.trimf*36000
        return result


   
    def get_trimf_of_current_month(self, brut_imposable):
        result = 0.0
        if brut_imposable < 50000:
            result = self.employee_id.trimf*75
        else:
            if brut_imposable < 83333:
                result = self.employee_id.trimf*300
            else:
                if brut_imposable < 166667:
                    result = self.employee_id.trimf*400
                else:
                    if brut_imposable < 583334:
                        result = self.employee_id.trimf*1000
                    else:
                        if brut_imposable < 1000000:
                            result = self.employee_id.trimf*1500
                        else:
                            result = self.employee_id.trimf*3000
        return result

    
    trimf_recal_mois_precedent = fields.Float(compute="_get_trimf_recal_mois_precedent",  invisible="1")
    
    api.depends('employee_id')
    def _get_trimf_recal_mois_precedent(self): 
        for payslip in self:
            two_last_payslip = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order="id desc", limit=2)
            if len(two_last_payslip) > 1:
                for payslip_precedent in two_last_payslip[1]:
                    payslip.trimf_recal_mois_precedent += sum(payslip_line.total for payslip_line in payslip_precedent.line_ids if payslip_line.code == "C7560")
            else:
                payslip.trimf_recal_mois_precedent = 0.0
           
            
    def get_cumul_trimf(self, brut_imposable_of_current_payslip):
        """ get the cumul genered by odoo """
        self.ensure_one()
        trimf_of_current_payslip = self.get_trimf_of_current_month(brut_imposable_of_current_payslip)
        for payslip in self:
            cumul_trimf = 0.0
            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], limit=12):
                if line.date_from.year == payslip.date_from.year:
                    cumul_trimf += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == "C7560")#somme des Somme des trimfs prélevées.
            cumul_trimf += trimf_of_current_payslip
            return cumul_trimf
        
    year = fields.Char(string="year", compute='_get_year', store=True)
    
    @api.depends('date_from')
    def _get_year(self):
        """ for recovering easyly the year of payslip"""
        for payslip in self:
            payslip.year = payslip.date_from.year
            
    def update_recompute_trimf(self):
        server_dt = DEFAULT_SERVER_DATE_FORMAT
        for payslip in self:
            year = datetime.strptime(str(payslip.date_from), server_dt).year

            ir_changed = 0
            two_last_payslip = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order="id desc", limit=2)
            # compute ir recal monthly
            if len(two_last_payslip) > 1:
                if two_last_payslip[1].nb_part_of_payslip != payslip.employee_id.ir:
                    ir_changed = 1#suivant la barème avec la nouvelle situation familiale
                    for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)]):#somme de ces fiches
                        if datetime.strptime(str(line.date_from), server_dt).year == year:
                            cumul_trimf_provisoire = 0.0
                            payslip_line_ids = self.env['hr.payslip.line'].search([('slip_id', '=', line.id)])
                            cumul_trimf_provisoire += sum(
                                payslip_line.total for payslip_line in payslip_line_ids if payslip_line.code == "C7510") #Recalcul de la TRIMF mensuelle (provisoire)

                            # update cumul TRIMF recaculer
                            #[trimf_recalcule.write({'amount': round(cumul_trimf_provisoire)}) for                                       #trimf_recalcule in payslip.line_ids if trimf_recalcule.code == "C7530"]
                            
                            
            if ir_changed == 1:
                # in case of regul monthly

                trimf_cumulees = 0.0
                somme_trimf_recalcule = 0.0
                cumul_trimf_provisoire = 0.0
                trimf_provisoire = 0.0
                trimf_recalcule_cumulees_current = 0.0
                for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)]):
                    if datetime.strptime(str(line.date_from), server_dt).year == year:
                        trimf_cumulees += sum(
                            payslip_line.total for payslip_line in line.line_ids 
                            if payslip_line.code == "C7520")
                        
                        somme_trimf_recalcule += sum(
                            payslip_line.total for payslip_line in line.line_ids 
                            if payslip_line.code == "C7530")#somme des trimf recal
                        
                        cumul_trimf_provisoire += sum(
                            payslip_line.total for payslip_line in line.line_ids 
                            if payslip_line.code == "C7510")#somme des trimf provisoire
                        
                        # update cumul TRIMF recalculées cumule
                        [trimf_recalcule_cumulees.write({'amount': round(somme_trimf_recalcule)}) for trimf_recalcule_cumulees in payslip.line_ids if trimf_recalcule_cumulees.code == "C7540"] 
                        
                        
                        # update trimf regul rule
                        [trimf_regul.write({'amount': round(cumul_trimf_provisoire - somme_trimf_recalcule)}) for trimf_regul in payslip.line_ids if trimf_regul.code == "C7550"] 
                        
                        for payslip_line in self.line_ids:
                            if payslip_line.code == "C7510":
                                trimf_provisoire = payslip_line.amount 
                                
                        for payslip_line in self.line_ids:
                            if payslip_line.code == "C7540":
                                trimf_recalcule_cumulees_current = payslip_line.amount         
                        
                 
                [obj.write({'amount': round(cumul_trimf_provisoire)}) for obj in
                 payslip.line_ids if obj.code == "C7520"]#trimf cumulee
                
                
                [obj.write({'amount': round(trimf_provisoire + (trimf_cumulees - trimf_recalcule_cumulees_current))}) for obj in
                 payslip.line_ids if obj.code == "C7560"]#trimf
                            
                            
                            
            