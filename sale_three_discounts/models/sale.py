from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    discount1 = fields.Float(
        'Discount 1 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )
    discount2 = fields.Float(
        'Discount 2 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )
    discount3 = fields.Float(
        'Discount 3 (%)',
        digits=dp.get_precision('Discount'),
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )
    discount = fields.Float(
        compute='get_discount',
        store=True,
        readonly=True,
        # agregamos states vacio porque lo hereda de la definicion anterior
        states={},
    )

    @api.one
    @api.depends('discount1', 'discount2', 'discount3')
    def get_discount(self):
        discount_factor = 1.0
        for discount in [self.discount1, self.discount2, self.discount3]:
            discount_factor = discount_factor * ((100.0 - discount) / 100.0)
        self.discount = 100.0 - (discount_factor * 100.0)

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(sale_order_line,
                    self)._prepare_invoice_line(qty)
        res.update({
            'discount1': self.discount1,
            'discount2': self.discount2,
            'discount3': self.discount3
        })
        return res
