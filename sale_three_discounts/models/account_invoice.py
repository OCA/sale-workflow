from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    discount1 = fields.Float(
        'Discount 1 (%)',
        digits=dp.get_precision('Discount'),
    )
    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
    )
    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
    )
    discount = fields.Float(
        compute='get_discount',
        store=True,
        readonly=True,
    )

    @api.one
    @api.depends('discount1', 'discount2', 'discount3')
    def get_discount(self):
        discount_factor = 1.0
        for discount in [self.discount1, self.discount2, self.discount3]:
            discount_factor = discount_factor * ((100.0 - discount) / 100.0)
        self.discount = 100.0 - (discount_factor * 100.0)
