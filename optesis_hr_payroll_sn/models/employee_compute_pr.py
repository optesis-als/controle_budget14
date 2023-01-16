from dateutil import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ProvisionRetraiteRuleInput(models.Model):
    _inherit = 'hr.payslip'

     
    #ind retraite
    def compute_brut_salaire_of_current_payslip(self, brut_salaire_of_current_payslip):
        for payslip in self:
            payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)])
            cumul_brut = 0.0
            for line in payslip_ids:
                cumul_brut += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == "C4000")       
                
            cumul_brut += brut_salaire_of_current_payslip 
            return round(cumul_brut * 0.07)
        

        
        
                
    def compute_provision_retraite(self, brut_salaire_of_current_payslip):
        for payslip in self:
            payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order='id desc',limit=12)
            #payslip_ids_precedent = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order='id desc',limit=11)
            if len(payslip_ids) >= 12:#si il fait 1ans ds l'entreprise
                cumul_brut = 0
                for line in payslip_ids:
                    cumul_brut += sum(line.total for line in line.details_by_salary_rule_category if
                                      line.code == 'C4000')  #obtenir cumul brut de ses 11 dernieres fiche

                # après les cumuls des 11 dernieres brut on y rajoute la valeur de la fiche de paie en cours
                cumul_brut += brut_salaire_of_current_payslip

                

               

                moy_brut = cumul_brut/len(payslip_ids)
                #difference entre les date 2 pour savoir l'ancienneté en année
                diff = relativedelta.relativedelta(payslip.contract_id.dateAnciennete, payslip.date_to)
                if diff.years <= 5:
                    provision_retraite = self.compute_pr_moin_cinq(moy_brut, -diff.years, -diff.months,
                                                                   -diff.days)  # moy_brut*(dur.days/360)*0.25 or dur=diff=payslip.date_to - payslip.contract_id.dateAnciennete

                elif 5 < diff.years <= 10:
                    provision_retraite = self.compute_pr_moin_cinq(moy_brut, 5, 0, 0)
                    provision_retraite += self.compute_pr_plus_cinq(moy_brut, -diff.years - 5, -diff.months,
                                                                    -diff.days)  # moy_brut*(dur.days/360)*0.3

                else:
                    provision_retraite = self.compute_pr_moin_cinq(moy_brut, 5, 0, 0)
                    provision_retraite += self.compute_pr_plus_cinq(moy_brut, -diff.years - 5, 0, 0)
                    provision_retraite += self.compute_pr_plus_dix(moy_brut, -diff.years - 10, -diff.months, -diff.days)

                return round(provision_retraite)
            return 0.0

    def compute_pr_moin_cinq(self, moyb, years, months, days):
        amount_for_year = (moyb * 0.25) * float(years)
        amount_for_month = moyb * 0.25 * (float(months) / 12)
        amount_for_days = moyb * 0.25 * (float(days) / 365)
        return round(amount_for_year + amount_for_month + amount_for_days)

    def compute_pr_plus_cinq(self, moyb, years, months, days):
        amount_for_year = (moyb * 0.3) * float(years)
        amount_for_month = moyb * 0.3 * (float(months) / 12)
        amount_for_days = moyb * 0.3 * (float(days) / 365)
        return round(amount_for_year + amount_for_month + amount_for_days)

    def compute_pr_plus_dix(self, moyb, years, months, days):
        amount_for_year = (moyb * 0.4) * float(years)
        amount_for_month = moyb * 0.4 * (float(months) / 12)
        amount_for_days = moyb * 0.4 * (float(days) / 365)
        return round(amount_for_year + amount_for_month + amount_for_days)

    
    def compute_retirement_balance(self, brut_salaire_of_current_payslip):
        for payslip in self:
            if payslip.contract_id.motif:
                return self.compute_provision_retraite(brut_salaire_of_current_payslip)
            
            
    
            
     
    def compute_indemnite_licenciement(self, brut_salaire_of_current_payslip):
        for payslip in self:
            payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order='id desc',limit=12)
           # payslip_ids_precedent = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order='id desc',limit=11)
            if len(payslip_ids) >= 12:#si il fait 1ans ds l'entreprise
                cumul_brut = 0
                for line in payslip_ids:
                    cumul_brut += sum(line.total for line in line.details_by_salary_rule_category if
                                      line.code == 'C4000')  #obtenir cumul brut de ses 11 dernieres fiche

                   
                # après les cumuls des 11 dernieres brut on y rajoute la valeur de la fiche de paie en cours
                cumul_brut += brut_salaire_of_current_payslip

               

                moy_brut = cumul_brut / len(payslip_ids)
                #difference entre les date 2 pour savoir l'ancienneté en année
                diff = relativedelta.relativedelta(payslip.contract_id.dateAnciennete, payslip.date_to)
                if diff.years <= 5:
                    indemnite_licenciement_calcul = self.compute_licenciement_moin_cinq(moy_brut, -diff.years, -diff.months,
                                                                   -diff.days)  # moy_brut*(dur.days/360)*0.25 or dur=diff=payslip.date_to - payslip.contract_id.dateAnciennete

                elif 5 < diff.years <= 10:
                    indemnite_licenciement_calcul = self.compute_licenciement_moin_cinq(moy_brut, 5, 0, 0)
                    indemnite_licenciement_calcul += self.compute_licenciement_plus_cinq(moy_brut, -diff.years - 5, -diff.months,
                                                                    -diff.days)  # moy_brut*(dur.days/360)*0.3

                else:
                    indemnite_licenciement_calcul = self.compute_licenciement_moin_cinq(moy_brut, 5, 0, 0)
                    indemnite_licenciement_calcul += self.compute_licenciement_plus_cinq(moy_brut, -diff.years - 5, 0, 0)
                    indemnite_licenciement_calcul += self.compute_licenciement_plus_dix(moy_brut, -diff.years - 10, -diff.months, -diff.days)

                return round(indemnite_licenciement_calcul)
            return 0.0

    def compute_licenciement_moin_cinq(self, moyb, years, months, days):
        amount_for_year = (moyb * 0.25) * float(years)
        amount_for_month = moyb * 0.25 * (float(months) / 12)
        amount_for_days = moyb * 0.25 * (float(days) / 365)
        return round(amount_for_year + amount_for_month + amount_for_days)

    def compute_licenciement_plus_cinq(self, moyb, years, months, days):
        amount_for_year = (moyb * 0.3) * float(years)
        amount_for_month = moyb * 0.3 * (float(months) / 12)
        amount_for_days = moyb * 0.3 * (float(days) / 365)
        return round(amount_for_year + amount_for_month + amount_for_days)

    def compute_licenciement_plus_dix(self, moyb, years, months, days):
        amount_for_year = (moyb * 0.4) * float(years)
        amount_for_month = moyb * 0.4 * (float(months) / 12)
        amount_for_days = moyb * 0.4 * (float(days) / 365)
        return round(amount_for_year + amount_for_month + amount_for_days)

    
   
        
    def compute_depart_retraite(self, retraire_of_current_payslip):
        for payslip in self:
            cumul_retraite = 0.0
            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)]):
                cumul_retraite += sum(payslip_line.total for payslip_line in line.line_ids 
                        if payslip_line.code == "C5520")#somme provision retraire

            cumul_retraite += retraire_of_current_payslip    
            return round(cumul_retraite) 
                
    def compute_indemnite_deces(self, retraire_of_current_payslip):
        for payslip in self:
            cumul_deces = 0.0
            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)]):
                cumul_deces += sum(payslip_line.total for payslip_line in line.line_ids 
                        if payslip_line.code == "C5520")#somme provision retraire

            cumul_deces += retraire_of_current_payslip    
            
            return round(cumul_deces) 
                