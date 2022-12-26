from odoo import _, api, fields, models
from odoo.exceptions import UserError

class PurchaseRequestLine(models.Model):

    _inherit = "purchase.request.line"

    account_id = fields.Many2one('account.account', string='Compte',domain=[('deprecated', '=', False)],
        help="The income or expense account related to the selected product.")

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(name, self.product_id.code)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
            self.account_id = account_id
        