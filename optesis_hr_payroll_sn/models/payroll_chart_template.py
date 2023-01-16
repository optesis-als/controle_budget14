# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, UserError
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class PayrollChartTemplate(models.Model):
    _name = "payroll.chart.template"
    _description = "Payroll Chart Template"

    name = fields.Char('Name')

    def load_for_current_company(self):
        """Installe les règles de paie sur la société actuelle, en remplacement
            l'existant s'il en avait déjà un défini.

            Notez également que cette fonction ne peut être exécutée que par une personne ayant l'administration
            droits.
        """
        self.ensure_one()
        company = self.env.user.company_id
        # Assurez-vous q tt est traduit dans la langue de l'entreprise, et non dans celle de l'utilisateur.
        self = self.with_context(lang=company.partner_id.lang)
        if not self.env.user._is_admin():
            #Seuls les administrateurs peuvent charger un plan comptable
            raise AccessError(_("Only administrators can load a chart of accounts"))

        

        # supprimer la règle salariale existante
        #for rules in self.env['hr.salary.rule'].search([('company_id', '=', company.id)]):
            #for record in rules:
                #rules_input = self.env['hr.rule.input'].search([('input_id', '=', record.id)])
                #[rule_input.unlink() for rule_input in rules_input]
            #record.unlink()


        # supprimer la catégorie de règles salariales existante
        #for rules_category in self.env['hr.salary.rule.category'].sudo().search([('company_id', '=', company.id)]):
            #[rule_category.unlink() for rule_category in rules_category]

        # créer règle et catégorie de salaire
        self._create_salary_rule_category(company)
        # creer regle de salaire
        self._create_salary_rule(company)
        
        
        company.chart_code = "sn"

        return {}
    #categorie
    def _create_salary_rule_category(self, company):
        self.ensure_one()
        rules_category = self.env['hr.salary.rule.category']
        for salary_rule_category in self.env['hr.salary.rule.category'].sudo().search([('company_id', '=', 1)]):

            category = [c for c in self.env['hr.salary.rule.category'].sudo().search(
                    [('company_id', '=', company.id), ('code', '=', salary_rule_category.code)])]

            rules_category += self.env['hr.salary.rule.category'].create({
                'name': salary_rule_category.name,
                'code': salary_rule_category.code,
                'parent_id': category[0].id if len(category) > 0 else False,
                'company_id': company.id,
            })
        return rules_category

    #regle
    def _create_salary_rule(self, company):
        self.ensure_one()
        salary_rules = self.env['hr.salary.rule']
        payroll_structure = self.env['hr.payroll.structure']

        for salary_rule in self.env['hr.salary.rule'].sudo().search([('company_id', '=', 1)]):
            # get the category
            category = [c for c in self.env['hr.salary.rule.category'].search(
                    [('company_id', '=', company.id), ('code', '=', salary_rule.category_id.code)])]

            rule_id = self.env['hr.salary.rule'].create({
                'name': salary_rule.name,
                'sequence': salary_rule.sequence,
                'code': salary_rule.code,
                'category_id': category[0].id,
                'condition_select': salary_rule.condition_select or False,
                'amount_select': salary_rule.amount_select or False,
                'amount_python_compute': salary_rule.amount_python_compute or False,
                'note': salary_rule.note or False,
                'appears_on_payslip': salary_rule.appears_on_payslip,
                'register_id': salary_rule.register_id.id or False,
                'parent_rule_id': salary_rule.parent_rule_id.id or False,
                'quantity': salary_rule.quantity,
                'amount_fix': salary_rule.amount_fix,
                'amount_percentage_base': salary_rule.amount_percentage_base or False,
                'condition_python': salary_rule.condition_python or False,
                'company_id': company.id,
            })

            # create rule input for the current salary rule in loop
            for rule_input in self.env['hr.rule.input'].sudo().search([('input_id', '=', salary_rule.id)]):
                self.env['hr.rule.input'].create({
                    'name': rule_input.name,
                    'code': rule_input.code,
                    'input_id': rule_id.id,
                    'company_id': company.id,
                })

            salary_rules += rule_id

        # create structure for salary rule
        payroll_structure += self.env['hr.payroll.structure'].create({
            'name': 'Base for new structures',
            'code': 'BASE',
            'company_id': company.id,
            'rule_ids': salary_rules,
            'parent_id': False,
        })


        company.write({'payroll_chart_template': self.id})
        return payroll_structure

    def _create_rule_input(self, company):
        self.ensure_one()
        inputs = self.env['hr.rule.input']
        for input_record in self.env['hr.rule.input'].search(('company_id', '=', 1)):
            inputs += self.env['hr.rule.input'].create({
                'code': input_record.name,
                'name': input_record.code,
                'input_id': input_record.input_id.id,
                'company_id': company.id,
            })
        return inputs
    



class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    payroll_chart_template = fields.Many2one(related='company_id.payroll_chart_template', string='Payroll Template', readonly=False, company_dependent=True)

    
    def set_values(self):
        """ installer un plan comptable pour l'entreprise donnée (si nécessaire)"""
        if self.payroll_chart_template and self.company_id.chart_code != 'sn':
            self.payroll_chart_template.load_for_current_company()
        super(ResConfigSettingsInherit, self).set_values()




class ResCompanyInherit(models.Model):
    _inherit = "res.company"

    payroll_chart_template = fields.Many2one('payroll.chart.template', company_dependent=True)
    chart_code = fields.Char()
