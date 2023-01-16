import time
from datetime import datetime, date, time as t
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError
from pytz import timezone


class HrSalaryRuleInherit(models.Model):
    _inherit = 'hr.salary.rule'

    is_prorata = fields.Boolean(string='Prorata', default=True,
                                help="Used to check if we apply prorata")


class BonusRuleInput(models.Model):
    _inherit = 'hr.payslip'
    
    
    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(BonusRuleInput, self).get_inputs(contract_ids, date_from, date_to)
        for bonus in self.contract_id.bonus:
            if not ((bonus.date_to < self.date_from or bonus.date_from > self.date_to) or
                    (bonus.date_to <= self.date_from or bonus.date_from >= self.date_to)):
                bonus_line = {
                    'name': str(bonus.salary_rule_id.name),
                    'code': bonus.salary_rule_id.code,
                    'contract_id': self.contract_id.id,
                    'amount': bonus.amount,

                }
                res += [bonus_line]
        return res
    
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
            
            for contract in contracts:
                employee = contract.employee_id
                localdict = dict(baselocaldict, employee=employee, contract=contract)
                for rule in sorted_rules:
                    key = rule.code + '-' + str(contract.id)
                    localdict['result'] = None
                    localdict['result_qty'] = 1.0
                    localdict['result_rate'] = 100
                    # check if the rule can be applied
                    if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                        # compute the amount of the rule
                        amount, qty, rate = rule._compute_rule(localdict)

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


            

           
