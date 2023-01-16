# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Treesa Maria Jude (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from odoo import models, fields

import time
from datetime import datetime, date, timedelta, time as t
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ir_changed = fields.Integer(default=0)
 
    relation_ids = fields.One2many('optesis.relation', 'employee_id', 'Relation')
    
    date_part_ir = fields.Datetime(compute="_get_compute_date_part_ir", string="Date part ir")
    
         
    
    @api.depends('relation_ids')
    def _get_compute_date_part_ir(self):
        for value in self:
            if value.relation_ids:
                for line in value.relation_ids:
                    if line.type == 'enfant': #si la relation est enfant
                        value.date_part_ir = line.birth
                    if line.type == 'conjoint': #si la relation est conjoint
                        value.date_part_ir = line.date_mariage 
                    else:
                        now = datetime.now()
                        value.date_relation_c  = now - timedelta(days=7300)    
            else:
                now = datetime.now()

                value.date_part_ir  = now - timedelta(days=7300)
            
  


    date_relation_c = fields.Datetime(compute="_get_compute_date_relation_c", string="Date relation conjoint")
    
         
    
    @api.depends('relation_ids')
    def _get_compute_date_relation_c(self):
        for value in self:
            if value.relation_ids:
                for line in value.relation_ids:
                    if line.type == 'conjoint': #si la relation est conjoint
                        value.date_relation_c = line.date_mariage 
                    else:
                        now = datetime.now()
                        value.date_relation_c  = now - timedelta(days=7300)
                 
            else:
                now = datetime.now()
                value.date_relation_c  = now - timedelta(days=7300)
                      

