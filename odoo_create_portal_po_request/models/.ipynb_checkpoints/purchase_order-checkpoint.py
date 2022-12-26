from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    prsit_portal_rfq_request_id = fields.Many2one(
        'rfq.purchase.requests',
    )
    is_rfq_request = fields.Boolean(
        'Is RFQ Request',
        copy=False,
    )

    def action_view_purchase_requests(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('odoo_create_portal_po_request.action_prsit_portal_purchase_order')
        action['domain'] = [('id', '=', self.prsit_portal_rfq_request_id.id)]
        return action
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    account_id = fields.Many2one('account.account', string='Compte',
        help="The income or expense account related to the selected product.")