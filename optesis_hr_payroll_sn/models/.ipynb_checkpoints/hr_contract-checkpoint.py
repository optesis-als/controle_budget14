import time, math
from datetime import datetime, date, time as t
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'
    
    
   
    motif = fields.Selection([('none', 'None'),('demission', 'Démission'), ('fin', 'Fin de contrat'), ('retraite', 'Retraite'),('licenciement', 'Licenciement'), ('deces', 'Décès'),
('depart_nogicie', 'Départ négocié')], string='Motif de sortie', default='none')