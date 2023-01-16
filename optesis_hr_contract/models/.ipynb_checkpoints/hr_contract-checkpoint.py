# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class Employee(models.Model):

    _inherit = "hr.employee"

    manager = fields.Boolean(string='Is a Manager')
    medic_exam = fields.Date(string='Medical Examination Date', groups="hr.group_hr_user")
    vehicle = fields.Char(string='Company Vehicle', groups="hr.group_hr_user")
    contract_ids = fields.One2many('hr.contract', 'employee_id', string='Employee Contracts')
    contract_id = fields.Many2one('hr.contract', string='Current Contract',domain="[('company_id', '=', company_id)]", help='Current contract of the employee')
    #state_contract = fields.Selection([
        #('draft', 'Nouveau'),
        #('open', 'En Cours'),
        #('pending', 'A renouveller'),
        #('close', 'Expiré'),
        #('cancel', 'Annulé')
    #], string='Status', compute='_onchangeEtat_contract')
    
    
    #@api.onchange('etat_contrat')
    #def _onchangeEtat_contract(self):
        #for r in self:
            #contracts = self.env['hr.contract'].search([('employee_id', '=', r.id)])
            #if contracts:
                #for rec in contracts:
                    #r.state_contract = rec.state
    
    calendar_mismatch = fields.Boolean(related='contract_id.calendar_mismatch')
    contracts_count = fields.Integer(compute='_compute_contracts_count', string='Contract Count')
    contract_warning = fields.Boolean(string='Contract Warning', store=True, compute='_compute_contract_warning')
    first_contract_date = fields.Date(compute='_compute_first_contract_date', groups="hr.group_hr_user")

    def _get_first_contracts(self):
        self.ensure_one()
        return self.sudo().contract_ids.filtered(lambda c: c.state != 'cancel')

    @api.depends('contract_ids.state', 'contract_ids.date_start')
    def _compute_first_contract_date(self):
        for employee in self:
            contracts = employee._get_first_contracts()
            if contracts:
                employee.first_contract_date = min(contracts.mapped('date_start'))
            else:
                employee.first_contract_date = False

    @api.depends('contract_id', 'contract_id.state', 'contract_id.kanban_state')
    def _compute_contract_warning(self):
        for employee in self:
            employee.contract_warning = not employee.contract_id or employee.contract_id.kanban_state == 'blocked' or employee.contract_id.state != 'open'

    def _compute_contracts_count(self):
        # read_group as sudo, since contract count is displayed on form view
        contract_data = self.env['hr.contract'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in contract_data)
        for employee in self:
            employee.contracts_count = result.get(employee.id, 0)

    def _get_contracts(self, date_from, date_to, states=['open'], kanban_state=False):
        """
        Returns the contracts of the employee between date_from and date_to
        """
        state_domain = [('state', 'in', states)]
        if kanban_state:
            state_domain = expression.AND([state_domain, [('kanban_state', 'in', kanban_state)]])

        return self.env['hr.contract'].search(
            expression.AND([[('employee_id', 'in', self.ids)],
            state_domain,
            [('date_start', '<=', date_to),
                '|',
                    ('date_end', '=', False),
                    ('date_end', '>=', date_from)]]))

    def _get_incoming_contracts(self, date_from, date_to):
        return self._get_contracts(date_from, date_to, states=['draft'], kanban_state=['done'])

    @api.model
    def _get_all_contracts(self, date_from, date_to, states=['open']):
        """
        Returns the contracts of all employees between date_from and date_to
        """
        return self.search([])._get_contracts(date_from, date_to, states=states)

    def write(self, vals):
        res = super(Employee, self).write(vals)
        if vals.get('contract_id'):
            for employee in self:
                employee.resource_calendar_id.transfer_leaves_to(employee.contract_id.resource_calendar_id, employee.resource_id)
                employee.resource_calendar_id = employee.contract_id.resource_calendar_id
        return res



class ContractType(models.Model):

    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'

    name = fields.Char(string='Contract Type', required=True, translate=True)
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)


class Contract(models.Model):

    _name = 'hr.contract'
    _description = 'Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    names_seq = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    
    @api.model
    def create(self, vals):
        if vals.get('names_seq', _('New')) == _('New'):
            vals['names_seq'] = self.env['ir.sequence'].next_by_code('hr.contract') or _('New')
        result = super(Contract, self).create(vals)
        return result

    
    @api.depends('employee_id.resource_calendar_id', 'resource_calendar_id')
    def _compute_calendar_mismatch(self):
        for contract in self:
            contract.calendar_mismatch = contract.resource_calendar_id != contract.employee_id.resource_calendar_id
            
    name = fields.Char('Contract Reference', required=True)
    active = fields.Boolean(default=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', string="Department")
    type_id = fields.Many2one('hr.contract.type', string="Employee Category", required=False, default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    job_id = fields.Many2one('hr.job', string='Job Position')
    date_start = fields.Date('Start Date', required=True, default=fields.Date.today,
        help="Start date of the contract.")
    date_end = fields.Date('End Date',
        help="End date of the contract (if it's a fixed-term contract).")
    trial_date_end = fields.Date('End of Trial Period',
        help="End date of the trial period (if there is one).")
    resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Working Schedule',
        default=lambda self: self.env['res.company']._company_default_get().resource_calendar_id.id)
    wage = fields.Monetary('Wage', digits=(16, 2), required=True, track_visibility="onchange", help="Employee's monthly gross wage.")
    advantages = fields.Text('Advantages')
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states',
       track_visibility='onchange', help='Status of the contract', default='draft')
    
    company_country_id = fields.Many2one('res.country', string="Company country", related='company_id.country_id', readonly=True)
    hr_responsible_id = fields.Many2one('res.users', 'HR Responsible', tracking=True,
        help='Person responsible for validating the employee\'s contracts.')
    calendar_mismatch = fields.Boolean(compute='_compute_calendar_mismatch')
    #first_contract_date = fields.Date(related='employee_id.first_contract_date')
    structure_type_id = fields.Many2one('hr.payroll.structure.type', string="Salary Structure Type")
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    permit_no = fields.Char('Work Permit No', related="employee_id.permit_no", readonly=False)
    visa_no = fields.Char('Visa No', related="employee_id.visa_no", readonly=False)
    visa_expire = fields.Date('Visa Expire Date', related="employee_id.visa_expire", readonly=False)
    reported_to_secretariat = fields.Boolean('Social Secretariat',
        help='Green this button when the contract information has been transfered to the social secretariat.')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.resource_calendar_id = self.employee_id.resource_calendar_id

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        if self.filtered(lambda c: c.date_end and c.date_start > c.date_end):
            raise ValidationError(_('Contract start date must be earlier than contract end date.'))

    @api.model
    def update_state(self):
        self.search([
            ('state', '=', 'open'),
            '|',
            '&',
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=7))),
            ('date_end', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
            '&',
            ('visa_expire', '<=', fields.Date.to_string(date.today() + relativedelta(days=60))),
            ('visa_expire', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ]).write({
            'state': 'pending'
        })

        self.search([
            ('state', 'in', ('open', 'pending')),
            '|',
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=1))),
            ('visa_expire', '<=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ]).write({
            'state': 'close'
        })

        return True

    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')
    ], string='Kanban State', default='normal', tracking=True, copy=False)
        
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'open' and 'kanban_state' in init_values and self.kanban_state == 'blocked':
            return self.env.ref('optesis_hr_contract.mt_contract_pending')
        elif 'state' in init_values and self.state == 'close':
            return self.env.ref('optesis_hr_contract.mt_contract_close')
        return super(Contract, self)._track_subtype(init_values)

