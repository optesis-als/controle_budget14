import time, math
from datetime import datetime, date, time as t
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrContractBonus(models.Model):
    _inherit = 'hr.contract'
    

   
    total_bonus = fields.Float(string="Total Bonus", compute="_get_bonus_amount", default="0", store=True)
    bonus = fields.One2many('hr.employee.bonus', 'contract_id', string="Bonus",
                            domain=[('state', '=', 'active')])
    #la fonction permet de calculer la somme des montants sur longlet element variable
    @api.depends('bonus.amount')
    def _get_bonus_amount(self):
        current_datetime = datetime.now()
        for contract in self:
            bonus_amount = 0
            for bonus in contract.bonus:
                x = datetime.strptime(str(bonus.date_from), '%Y-%m-%d')
                y = datetime.strptime(str(bonus.date_to), '%Y-%m-%d')
                if x <= current_datetime <= y:
                    bonus_amount = bonus_amount + bonus.amount
                contract.total_bonus = bonus_amount
