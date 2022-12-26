# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _name = 'rfq.purchase.requests'
    _description = 'Purchase Request'
    _inherits = {'purchase.order': 'purchase_order_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'priority desc, id desc'

    

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('rfq.purchase.requests', sequence_date=seq_date) or '/'
        vals['partner_id'] = self.env.user.partner_id.id
        res = super(PurchaseOrder, self_comp).create(vals)
        res.purchase_order_id.is_rfq_request = True
        return res

    # @api.model
    # def default_get(self, fields):
    #     res = super(PurchaseOrder, self).default_get(fields)
    #     res.update({'partner_id': self.env.user.partner_id.id})
    #     return res

    is_created_from_webrfq_prsit = fields.Boolean(
        string="Is Created from Web RFC PRSIT",
        default=False,
    )

    rfq_created_by_id_prsit = fields.Many2one(
        'res.users',
        string="RFQ Created By PRSIT",
        default=lambda self: self.env.user,
    )

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string="Purchase Request",
        ondelete="cascade",
        required=True,
        auto_join=True,
        index=True
    )

    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('approve', 'Approved'),
            ('purchase', 'RFQ'),
            ('reject', 'Rejected'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        readonly=True,
        index=True,
        copy=False,
        default='draft',
        ondelete={'draft': 'cascade', 'approve': 'cascade', 'cancel': 'cascade', 'purchase': 'cascade'}
    )

    approver_id = fields.Many2one(
        'hr.employee',
        string="Approver"
    )

    date_order = fields.Date('Order Deadline', required=True, index=True, copy=False,
                                 default=fields.Date.today,
                                 help="Depicts the date within which the Quotation should be confirmed and converted into a purchase order.")

#    prsit_portal_purchase_order_count = fields.Integer(
#        compute="_compute_prsit_portal_purchase_order_count",
#        string="Prsit Portal Purchase Order Count",
#        copy=False,
#        default=0,
#        store=True
#    )

    portal_purchase_id = fields.Integer('Purchase Order ID')
    
    def action_prsit_portal_purchase_order_link_po(self):
        res = self.env['ir.actions.act_window']._for_xml_id('purchase.action_rfq_form')
        res['res_id'] = self.portal_purchase_id
        res['res_model'] = 'purchase.order'
        res['target'] = 'current'
        return res

    def _prepare_purchase_order_values(self, rec):
        product_qty_list = []
        for line in rec.order_line:
            product_qty_list.append((0, 0, {
                'name': line.name,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'price_unit': line.price_unit, # added as not update
                'account_id':rec.order_line.account_id.id,
            }))
            account_id_val = rec.order_line.account_id.id
        _logger.info('ANTA mougneul rek yalla bakhna %s',account_id_val)

        return {
            'partner_id': rec.partner_id.id,
            #'account_id':account_id_val,
            'order_line': product_qty_list,
            'prsit_portal_rfq_request_id': rec.id,
        }

    def action_button_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_button_approve(self):
        for rec in self:
            # values = self._prepare_purchase_order_values(rec)
            # purchase_id = self.env['purchase.order'].create(values)
            # purchase_id.button_confirm()
            # self.portal_purchase_id = purchase_id.id
            rec.state = 'approve'

    def action_create_purchase_order(self):
        for rec in self:
            values = self._prepare_purchase_order_values(rec)
            purchase_id = self.env['purchase.order'].create(values)
            rec.portal_purchase_id = purchase_id.id
            rec.state = 'purchase'


    def action_button_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_button_purchase(self):
        for rec in self:
            rec.state = 'purchase'
    
    def action_button_reject(self):
        for rec in self:
            rec.state = 'reject'
    
    def action_button_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

#    def _compute_prsit_portal_purchase_order_count(self):
#        for rec in self:
#            rec.prsit_portal_purchase_order_count = len(self.env['rfq.purchase.requests'].search([('is_created_from_webrfq_prsit', '=', True)]))
