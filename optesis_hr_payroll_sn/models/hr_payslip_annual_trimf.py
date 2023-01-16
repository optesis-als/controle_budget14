import time
from datetime import datetime, date, timedelta, time as t
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError


class HrPayslipInheritTrimf(models.Model):
    _inherit = 'hr.payslip'
    
    
    
   
    def get_annual_trimf(self, brut_imposable_of_current_payslip):
        for payslip in self:
            brut_impo_annual = 0.0
            result = 0.0
            cumul_brut = 0.0
            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id), ('year', '=', payslip.date_from.year)]):
                if line.date_from.year == payslip.date_from.year:
                    cumul_brut += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == "C4500")#BRUT Imposable et cumul imposable  on la mm formule
            
            brut_impo_annual = cumul_brut+brut_imposable_of_current_payslip
            #raise ValidationError(_(brut_impo_annual))
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


   
    #def get_trimf_of_current_month(self, brut_imposable):
        #result = 0.0
        #if brut_imposable < 50000:
            #result = self.employee_id.trimf*75
        #lse:
            #if brut_imposable < 83333:
                #result = self.employee_id.trimf*300
            #else:
                #if brut_imposable < 166667:
                    #result = self.employee_id.trimf*400
                #else:
                    #if brut_imposable < 583334:
                        #result = self.employee_id.trimf*1000
                    #else:
                        #if brut_imposable < 1000000:
                            #result = self.employee_id.trimf*1500
                        #else:
                            #result = self.employee_id.trimf*3000
        #return result

    
   
           
            
    #def get_cumul_trimf(self, brut_imposable_of_current_payslip):
        #self.ensure_one()
        #trimf_of_current_payslip = self.get_trimf_of_current_month(brut_imposable_of_current_payslip)
        #for payslip in self:
            #c_trimf = 0.0
            #for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], limit=12):
                #if line.date_from.year == payslip.date_from.year:
                    #c_trimf += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == #"C7560")#somme des Somme des trimfs prélevées.
            #c_trimf += trimf_of_current_payslip
            #return c_trimf
            
     #condition1: if la date date du relation == date de la feuille et state == 'draft' dc on cacul le ir 
    
    #On récupérer la date de la dernière relation
    date_relation_c = fields.Datetime(string="Date relation conjoint",  invisible="1", related="employee_id.date_relation_c")
    
    year = fields.Char(string="year", compute='_get_year', store=True)
    
    @api.depends('date_from')
    def _get_year(self):
        """ for recovering easyly the year of payslip"""
        for payslip in self:
            payslip.year = payslip.date_from.year
            
    def get_trimf_recalculer(self):
        server_dt = DEFAULT_SERVER_DATE_FORMAT
        for payslip in self:
            year = datetime.strptime(str(payslip.date_from), server_dt).year
            
            trimf_rec = 0.0
            ir_changed = 0
            trimf_pro = 0.0

            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order="id desc", limit=12):
                if datetime.strptime(str(line.date_from), server_dt).year == year:
                  
                    if payslip.date_from.year == payslip.date_relation_c.year:       
                        if payslip.date_from.month == payslip.date_relation_c.month:

                            payslip_line_ids = self.env['hr.payslip.line'].search([('slip_id', '=', line.id)])

                            trimf_pro = sum(payslip_line.total for payslip_line in payslip.line_ids if payslip_line.code == "C4550")
                            
                            
                            
                            for payslip_line in payslip.line_ids:
                                if payslip_line.code == "C7530": #trimf recal

                                    if trimf_pro < 50000:
                                        trimf_rec = self.employee_id.trimf*75
                                    else:
                                        if trimf_pro < 83333:
                                            trimf_rec = self.employee_id.trimf*300
                                        else:
                                            if trimf_pro < 166667:
                                                trimf_rec = self.employee_id.trimf*400
                                            else:
                                                if trimf_pro < 583334:
                                                    trimf_rec = self.employee_id.trimf*1000
                                                else:
                                                    if trimf_pro < 1000000:
                                                        trimf_rec = self.employee_id.trimf*1500
                                                    else:
                                                      trimf_rec = self.employee_id.trimf*3000
                                    # update ir_recal
                                    obj = self.env['hr.payslip.line'].search(
                                    [('code', '=', payslip_line.code), ('slip_id', '=', line.id)], limit=1)
                                    if obj:
                                        obj.write({'amount': round(trimf_rec)})         
            
    def update_recompute_trimf(self):
        server_dt = DEFAULT_SERVER_DATE_FORMAT
        for payslip in self:
            year = datetime.strptime(str(payslip.date_from), server_dt).year

            
                        
            trimf_cumulees = 0.0
            somme_trimf_recalcule = 0.0
            cumul_trimf_provisoire = 0.0
            trimf_provisoire = 0.0
            trimf_regul_current = 0.0
            cumul_trimf_recalcul = 0.0
            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)]):
                if datetime.strptime(str(line.date_from), server_dt).year == year:
                  
                    somme_trimf_recalcule += sum(
                                    payslip_line.total for payslip_line in line.line_ids 
                                    if payslip_line.code == "C7530")#somme des trimf recal

                    cumul_trimf_provisoire += sum(
                                    payslip_line.total for payslip_line in line.line_ids 
                                    if payslip_line.code == "C7510")#somme des trimf provisoire

                    # update trimf regul 
                    [trimf_regul.write({'amount': round(cumul_trimf_provisoire - somme_trimf_recalcule)}) for trimf_regul in payslip.line_ids if trimf_regul.code == "C7550"] 
                    
                    cumul_trimf_recalcul += sum(
                                    payslip_line.total for payslip_line in line.line_ids 
                                    if payslip_line.code == "C7530")#somme des trimf recal


                    for payslip_line in self.line_ids:
                        if payslip_line.code == "C7510":
                            trimf_provisoire = payslip_line.amount 

                   
                    for payslip_line in self.line_ids:
                        if payslip_line.code == "C7550":
                            trimf_regul_current = payslip_line.amount            


                    

                    [obj.write({'amount': round(trimf_provisoire - trimf_regul_current)}) for obj                     in payslip.line_ids if obj.code == "C7560"]#trimf
                    
                    [obj.write({'amount': round(cumul_trimf_provisoire)}) for obj in
                    payslip.line_ids if obj.code == "C7520"]#trimf cumulee
                    
                    # update TRIMF recalculées cumule
                    [trimf_recalcule_cumulees.write({'amount': round(cumul_trimf_recalcul)}) for trimf_recalcule_cumulees in payslip.line_ids if trimf_recalcule_cumulees.code == "C7540"] 






            