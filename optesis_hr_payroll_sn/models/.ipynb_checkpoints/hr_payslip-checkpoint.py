import time
from datetime import datetime, date, timedelta, time as t
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError
from pytz import timezone


class PayslipRule(models.Model):
    _inherit = 'hr.payslip'
    
    payslip_count = fields.Float(string="indeminité depart à la retraite", compute="_nbr_payslip")
    
   
    api.depends('employee_id')
    def _nbr_payslip(self):
         for payslip in self:
             payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)])
             payslip.payslip_count = len(payslip_ids) 
                
                
                
    
    provision_retraite_current = fields.Float(string="current retraite", compute="_get_provision_retraite_current")
    
   
    api.depends('employee_id')
    def _get_provision_retraite_current(self):
        for payslip in self:
            payslip.provision_retraite_current += sum(payslip_line.total for payslip_line in payslip.line_ids if payslip_line.code == "C5520")# 
                
            
    provision_retraite_all = fields.Float(string="indeminité depart à la retraite", compute="_get_provision_retraite_all")
    
   
    api.depends('employee_id')
    def _get_provision_retraite_all(self):
         for payslip in self:
            payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)])
            cumul_provision_retraite_all = 0.0
            for line in payslip_ids:
                cumul_provision_retraite_all += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == "C5520")# 
                payslip.provision_retraite_all = cumul_provision_retraite_all 
                
    
    
    ir_recalcule_cumul = fields.Float(string="brut current", compute="_get_ir_recalcule_cumul")
    
   
    api.depends('employee_id')
    def _get_ir_recalcule_cumul(self):
        for payslip in self:
            payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)])
            cumul_ir_recal = 0.0
            for line in payslip_ids:
                cumul_ir_recal += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == "C7030")# IR RECALCULE
                payslip.ir_recalcule_cumul = cumul_ir_recal
                
               
                
                
    
        
        
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
            payslip.update_recompute_ir()
            payslip.update_recompute_trimf()
            
            
        return True
    
    
             
            
            
    nb_part_of_payslip = fields.Float(string="Nb part", compute="_get_nb_part_of_payslip", states={'done': [('readonly', True)]}, store=True)
    
    api.depends('employee_id')
    def _get_nb_part_of_payslip(self):
        for payslip in self:
            if payslip.employee_id:
                payslip.nb_part_of_payslip = payslip.employee_id.ir
                
 
   
  
        
        
    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        for record in self:
            def _sum_salary_rule_category(localdict, category, amount):
                if category.parent_id:
                    localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
                if category.code in localdict['categories'].dict:
                    amount += localdict['categories'].dict[category.code]
                localdict['categories'].dict[category.code] = amount
                return localdict

            class BrowsableObject(object):
                def __init__(record, employee_id, dict, env):
                    record.employee_id = employee_id
                    record.dict = dict
                    record.env = env

                def __getattr__(record, attr):
                    return attr in record.dict and record.dict.__getitem__(attr) or 0.0

            class InputLine(BrowsableObject):
                """a class that will be used into the python code, mainly for usability purposes"""

                def sum(record, code, from_date, to_date=None):
                    if to_date is None:
                        to_date = fields.Date.today()
                    record.env.cr.execute("""
                            SELECT sum(amount) as sum
                            FROM hr_payslip as hp, hr_payslip_input as pi
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                          (record.employee_id, from_date, to_date, code))
                    return self.env.cr.fetchone()[0] or 0.0

            class WorkedDays(BrowsableObject):
                """a class that will be used into the python code, mainly for usability purposes"""

                def _sum(record, code, from_date, to_date=None):
                    if to_date is None:
                        to_date = fields.Date.today()
                    record.env.cr.execute("""
                            SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                            FROM hr_payslip as hp, hr_payslip_worked_days as pi
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                          (record.employee_id, from_date, to_date, code))
                    return record.env.cr.fetchone()

                def sum(record, code, from_date, to_date=None):
                    res = record._sum(code, from_date, to_date)
                    return res and res[0] or 0.0

                def sum_hours(record, code, from_date, to_date=None):
                    res = record._sum(code, from_date, to_date)
                    return res and res[1] or 0.0

            class Payslips(BrowsableObject):
                """a class that will be used into the python code, mainly for usability purposes"""

                def sum(record, code, from_date, to_date=None):
                    if to_date is None:
                        to_date = fields.Date.today()
                    record.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                                    FROM hr_payslip as hp, hr_payslip_line as pl
                                    WHERE hp.employee_id = %s AND hp.state = 'done'
                                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                                          (record.employee_id, from_date, to_date, code))
                    res = record.env.cr.fetchone()
                    return res and res[0] or 0.0

            # we keep a dict with the result because a value can be overwritten by another rule with the same code
            result_dict = {}
            rules_dict = {}
            worked_days_dict = {}
            inputs_dict = {}
            blacklist = []
            payslip = record.env['hr.payslip'].browse(payslip_id)
            for worked_days_line in payslip.worked_days_line_ids:
                worked_days_dict[worked_days_line.code] = worked_days_line
            for input_line in payslip.input_line_ids:
                inputs_dict[input_line.code] = input_line

            categories = BrowsableObject(payslip.employee_id.id, {}, record.env)
            inputs = InputLine(payslip.employee_id.id, inputs_dict, record.env)
            worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, record.env)
            payslips = Payslips(payslip.employee_id.id, payslip, record.env)
            rules = BrowsableObject(payslip.employee_id.id, rules_dict, record.env)

            baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days,
                             'inputs': inputs}
            # get the ids of the structures on the contracts and their parent id as well
            contracts = record.env['hr.contract'].browse(contract_ids)
            structure_ids = contracts.get_all_structures()
            # get the rules of the structure and thier children
            rule_ids = record.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
            # run the rules by sequence
            # Appending bonus rules from the contract
            for contract in contracts:
                for bonus in contract.bonus:
                    if not ((bonus.date_to < record.date_from or bonus.date_from > record.date_to)
                            or (bonus.date_to <= record.date_from or bonus.date_from >= record.date_to)):
                        if bonus.salary_rule_id.is_prorata:
                            bonus.salary_rule_id.write({
                                'amount_fix': round(bonus.amount * (worked_days.WORK100.number_of_days) / self.number_of_days_work), })
                        else:
                            bonus.salary_rule_id.write({'amount_fix': round(bonus.amount)})
                        rule_ids.append((bonus.salary_rule_id.id, bonus.salary_rule_id.sequence))

            sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
            sorted_rules = record.env['hr.salary.rule'].browse(sorted_rule_ids)
            
            #add diw pour calcul de regle salarial du payroll_sn
            brut_of_current_payslip = 0.0
            brut_imposable_of_current_payslip = 0.0
            ir_of_current_payslip = 0.0
            brut_salaire_of_current_payslip = 0.0
            retraire_of_current_payslip = 0.0
            #fin diw pour regle salarial du payroll_sn
            for contract in contracts:
                employee = contract.employee_id
                localdict = dict(baselocaldict, employee=employee, contract=contract)
                for rule in sorted_rules:
                    key = rule.code + '-' + str(contract.id)
                    localdict['result'] = None
                    localdict['result_qty'] = 1.0
                    localdict['result_rate'] = 100
                    520# check if the rule can be applied
                    if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                        # compute the amount of the rule
                        amount, qty, rate = rule._compute_rule(localdict)
                        
                        #add diw pour calcul de regle salarial du payroll_sn
                        
                        if rule.category_id.code == 'INDM' or rule.category_id.code == 'BASE' or \
                                rule.category_id.code == 'NIMP':
                            brut_of_current_payslip += amount #somme des regle avec comme code de categories BASE, INDM, NIMP
                        
                        
                        # get brut of current payslip
                        if rule.code == 'C4000':
                            brut_salaire_of_current_payslip += amount
                            
                       
                        # get brut imposable of current payslip
                        if rule.code == 'C7510':
                            brut_imposable_of_current_payslip = amount
                            
                            
                        # get ir provisoire of current payslip
                        if rule.code == 'C7010':
                            ir_of_current_payslip = amount
                            
                        # get provision retraire of current payslip
                        if rule.code == 'C5520':
                            retraire_of_current_payslip = amount
                           
                            
                            
                            
                        if rule.code == 'C7020': # get cumul ir
                            amount = payslip.get_cumul_ir(ir_of_current_payslip)
                            
                        #regle lié au fonction
                        #if rule.code == 'C2161': # get ir annuel
                            #amount = payslip.get_ir_annuel(brut_imposable_of_current_payslip)
                        
                        #if rule.code == 'C2048': # get the trimf annual
                            #amount = payslip.get_annual_trimf()
                        #if rule.code == 'C7520': # get cumul trimf
                            #amount = payslip.get_cumul_trimf(brut_imposable_of_current_payslip)
                            
                        if rule.code == 'C5520':
                            amount = payslip.compute_provision_retraite(brut_of_current_payslip)
                        #regles lié au motif de sorti    
                        if rule.code == 'C3050':  # Indemnité de départ à la retraite
                            amount = payslip.compute_depart_retraite(retraire_of_current_payslip)
                        elif rule.code == 'C3030':  # indemnite de licenciement
                            amount = payslip.compute_indemnite_licenciement(brut_of_current_payslip)
                        elif rule.code == 'C3040':  # indemnite de deces 
                            amount = payslip.compute_indemnite_deces(brut_of_current_payslip)     
                        elif rule.code == 'C2030':  # indemnite de fin de contrat
                            amount = payslip.compute_brut_salaire_of_current_payslip( brut_salaire_of_current_payslip)
                            
                        
                        else:
                            pass

                        # check if there is already a rule computed with that code
                        previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                        # set/overwrite the amount computed for this rule in the localdict
                        tot_rule = amount * qty * rate / 100.0
                        localdict[rule.code] = tot_rule
                        rules_dict[rule.code] = rule
                        # sum the amount for its salary category
                        localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                        # create/overwrite the rule in the temporary results
                        result_dict[key] = {
                            'salary_rule_id': rule.id,
                            'contract_id': contract.id,
                            'name': rule.name,
                            'code': rule.code,
                            'category_id': rule.category_id.id,
                            'sequence': rule.sequence,
                            'appears_on_payslip': rule.appears_on_payslip,
                            'condition_select': rule.condition_select,
                            'condition_python': rule.condition_python,
                            'condition_range': rule.condition_range,
                            'condition_range_min': rule.condition_range_min,
                            'condition_range_max': rule.condition_range_max,
                            'amount_select': rule.amount_select,
                            'amount_fix': rule.amount_fix,
                            'amount_python_compute': rule.amount_python_compute,
                            'amount_percentage': rule.amount_percentage,
                            'amount_percentage_base': rule.amount_percentage_base,
                            'register_id': rule.register_id.id,
                            'amount': amount,
                            'employee_id': contract.employee_id.id,
                            'quantity': qty,
                            'rate': rate,
                        }
                    else:
                        # blacklist this rule and its children
                        blacklist += [id for id, seq in rule._recursive_search_of_rules()]
                # payslips.contract_id._get_duration(payslips.date_from)

            return [value for code, value in result_dict.items()]


            

   #par diw: On veut connaitre la feuille ou on veut ajouter le calcul du ir
    #si la date X du relation == a la date X de la feuille et state == 'draft' dc on cacul , Sinon on le calcul sur la feuille du mois suivant  X + 1 
    
    

   
    
    #condition1: if la date date du relation == date de la feuille et state == 'draft' dc on cacul le ir laba
    
    #On récupérer la date de la dernière relation
    date_part_ir = fields.Datetime(string="Date part ir",  invisible="1", related="employee_id.date_part_ir")
    

    #condition2: else: si la date date X + 1 (date_part_ir_mois_suivant) == date de la feuille et si le ir n'etait pas calculé sur la condition1 donc on le calcul pour la feuille mois prochaine
    
    #sur la date du dernier relation on ny ajoute 30 pour connaitre le mois suivant apres un relation
    date_part_ir_mois_suivant =  fields.Datetime(compute="_get_compute_mois_suivant", string="Date part ir mois suivant",  invisible="1")
   
    duration_un_mois = fields.Float(default=30, help="Duration dans 1mois")



    @api.depends('date_part_ir', 'duration_un_mois')
    def _get_compute_mois_suivant(self):
        for r in self:
            if not (r.date_part_ir and r.duration_un_mois):
                r.date_part_ir_mois_suivant = r.date_part_ir
                continue
            duration_un_mois = timedelta(days = r.duration_un_mois, seconds=-1)
            r.date_part_ir_mois_suivant = r.date_part_ir + duration_un_mois
            
            
    #diw : on verifions si le ir est calculer pour la feuille précédente
    
    ir_mois_precedent = fields.Float(compute="_get_ir_mois_precedent",  invisible="1")
    
    api.depends('employee_id')
    def _get_ir_mois_precedent(self): 
        for payslip in self:
            two_last_payslip = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order="id desc", limit=2)
            if len(two_last_payslip) > 1:
                for payslip_precedent in two_last_payslip[1]:
                    payslip.ir_mois_precedent += sum(payslip_line.total for payslip_line in payslip_precedent.line_ids if payslip_line.code == "C7050")
            else:
                payslip.ir_mois_precedent = 0.0
           
    
    def update_recompute_ir(self):
        server_dt = DEFAULT_SERVER_DATE_FORMAT
        for payslip in self:
            year = datetime.strptime(str(payslip.date_from), server_dt).year

            two_last_payslip = self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order="id desc", limit=12)#on doit le remplacé par 12
            # compute ir recal monthly
            if len(two_last_payslip) >= 12: #on doit le remplacé par 12
                if payslip.employee_id.ir: #on recupére le ir lié a lemployee
                    for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], order="id desc", limit=2):
                        
                        #l'année du fiche doit etre l'année en cour
                        if datetime.strptime(str(line.date_from), server_dt).year == year:
                            cumul_tranche_ipm = 0.0
                            deduction = 0.0
                            payslip_line_ids = self.env['hr.payslip.line'].search([('slip_id', '=', line.id)])
                           
                            
                            cumul_tranche_ipm += sum(payslip_line.total for payslip_line in payslip_line_ids if payslip_line.code == "C7060")
                            
                           
                            for payslip_line in payslip_line_ids:
                                if payslip_line.code == "C7030": #recal
                                    obj_empl = self.env['hr.employee'].browse(payslip.employee_id.id)
                                    if obj_empl:
                                        if payslip.employee_id.ir == 1:
                                            deduction = 0.0

                                        if payslip.employee_id.ir == 1.5:
                                            if cumul_tranche_ipm * 0.1 < 8333:
                                                deduction = 8333
                                            elif cumul_tranche_ipm * 0.1 > 25000:
                                                deduction = 25000
                                            else:
                                                deduction = cumul_tranche_ipm * 0.1

                                        if payslip.employee_id.ir == 2:
                                            if cumul_tranche_ipm * 0.15 < 16666.66666666667:
                                                deduction = 16666.66666666667
                                            elif cumul_tranche_ipm * 0.15 > 54166.66666666667:
                                                deduction = 54166.66666666667
                                            else:
                                                deduction = cumul_tranche_ipm * 0.15 #43224,9

                                        if payslip.employee_id.ir == 2.5:
                                            if cumul_tranche_ipm * 0.2 < 25000:
                                                deduction = 25000
                                            elif cumul_tranche_ipm * 0.2 > 91666.66666666667:
                                                deduction = 91666.66666666667
                                            else:
                                                deduction = cumul_tranche_ipm * 0.2

                                        if payslip.employee_id.ir == 3:
                                            if cumul_tranche_ipm * 0.25 < 33333.33333333333:
                                                deduction = 33333.33333333333
                                            elif cumul_tranche_ipm * 0.25 > 137500:
                                                deduction = 137500
                                            else:
                                                deduction = cumul_tranche_ipm * 0.25

                                        if payslip.employee_id.ir == 3.5:
                                            if cumul_tranche_ipm * 0.3 < 41666.66666666667:
                                                deduction = 41666.66666666667
                                            elif cumul_tranche_ipm * 0.3 > 169166.6666666667:
                                                deduction = 169166.6666666667
                                            else:
                                                deduction = cumul_tranche_ipm * 0.3

                                        if payslip.employee_id.ir == 4:
                                            if cumul_tranche_ipm * 0.35 < 50000:
                                                deduction = 50000
                                            elif cumul_tranche_ipm * 0.35 > 207500:
                                                deduction = 207500
                                            else:
                                                deduction = cumul_tranche_ipm * 0.35

                                        if payslip.employee_id.ir == 4.5:
                                            if cumul_tranche_ipm * 0.4 < 58333.33333:
                                                deduction = 58333.33333
                                            elif cumul_tranche_ipm * 0.4 > 229583.3333:
                                                deduction = 229583.3333
                                            else:
                                                deduction = cumul_tranche_ipm * 0.4

                                        if payslip.employee_id.ir == 5:
                                            if cumul_tranche_ipm * 0.45 < 66666.66667:
                                                deduction = 66666.66667
                                            elif cumul_tranche_ipm * 0.45 > 265000:
                                                deduction = 265000
                                            else:
                                                deduction = cumul_tranche_ipm * 0.45

                                        if cumul_tranche_ipm - deduction > 0:
                                            ir_val_recal = cumul_tranche_ipm - deduction
                                            #nous avons ir =2 cumul_tranche_ipm =288166 dc deduction=288166*0.15
                                            
                                    
                                        else:
                                            ir_val_recal = 0
                                        # update ir_recal
                                        
                                        [obj.write({'amount': round(10000)}) for obj in
                         payslip.line_ids if obj.code == "C7030"]#regul
                                        
                                        obj = self.env['hr.payslip.line'].search(
                                            [('code', '=', payslip_line.code), ('slip_id', '=', line.id)], limit=1) 
                                        if obj:
                                            obj.write({'amount': round(ir_val_recal)})
                                            
            # end compute ir_recal

            ir_payslip = 0.0
            net_payslip = 0.0
            ir_payslip += sum(payslip_line.total for payslip_line in payslip.line_ids if
                              payslip_line.code == "C7010")#ir PROVISOIRE
            
            net_payslip += sum(payslip_line.total for payslip_line in payslip.line_ids if
                               payslip_line.code == "C9000")#net

           
            cumul_ir = 0.0
            cumul_ir_recal = 0.0
            cumul_ir_recalcul = 0.0
            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)]):
                if datetime.strptime(str(line.date_from), server_dt).year == year:
                    
                    
                    
                    cumul_ir += sum(payslip_line.total for payslip_line in line.line_ids if
                                         payslip_line.code == "C7010") #ir provisoire
                    
                    
                    cumul_ir_recal += sum(payslip_line.total for payslip_line in line.line_ids if
                            payslip_line.code == "C7030")#ir recal = ir_val_recal
                    
                    
                    # update ir regul rule
                    [obj.write({'amount': round(cumul_ir - cumul_ir_recal)}) for obj in
                         payslip.line_ids if obj.code == "C7050"]#regul
                    
                    cumul_ir_recalcul += sum(
                            payslip_line.total for payslip_line in line.line_ids 
                            if payslip_line.code == "C7030")#somme ir recal
                    
                    # update ir regul rule
                    [obj.write({'amount': round(cumul_ir - cumul_ir_recal)}) for obj in
                         payslip.line_ids if obj.code == "C7040"]#ir recalculer cumul
                    
                    
                # update ir_fin(Impôt sur le revenu)
                #ir_regul + ir_provisoire
                [obj.write({'amount': round(cumul_ir + (cumul_ir - cumul_ir_recal))}) for obj in
                 payslip.line_ids if obj.code == "C7099"]#Impôt sur le revenu
            else:
                [obj.write({'amount': round(ir_payslip)}) for obj in
                payslip.line_ids if obj.code == "C7099"]#Impôt sur le revenu
   
            # in case of regul yearly
            #regul_annuel = [obj for obj in payslip.line_ids if obj.code == 'C2163'] # recover year regul rule
            #if len(regul_annuel) > 0: # check if year rugul rule exist
                #[obj.write({'amount': round(ir_payslip - regul_annuel[0].total)}) for obj in
                #payslip.line_ids if obj.code == "C7099"]
                    
            # defalquer ir_fin du net
            #ir_fin = 0.0
            #ir_fin += sum(payslip_line.total for payslip_line in payslip.line_ids if
                          #payslip_line.code == "C7099")
            #[obj.write({'amount': round(net_payslip - ir_fin)}) for obj in
            #payslip.line_ids if obj.code == "C9000"]
                       

        