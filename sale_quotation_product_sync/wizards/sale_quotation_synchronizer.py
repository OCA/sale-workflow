# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class SaleQuotationSynchronizer(models.TransientModel):

    _name = 'sale.quotation.synchronizer'
    _description = 'Synchronize quotations from product'

    product_ids = fields.Many2many('product.product')

    sync_sale_order_line = fields.Boolean(
        string='Sync draft order lines', default=True,
    )
    sync_sale_quote_line = fields.Boolean(
        string='Sync quotation template lines', default=True,
    )
    sync_sale_quote_option = fields.Boolean(
        string='Sync quotation template options', default=True,
    )

    sync_price_unit = fields.Boolean(
        string='Sync unit price', default=True, readonly=True,
    )

    def _sync_sale_order_lines(self, product):
        sale_order_lines = self.env['sale.order.line'].search(
            [
                ('product_id', '=', product.id),
                ('order_id.state', '=', 'draft')
            ]
        )
        for order_line in sale_order_lines:
            new_price = product.lst_price
            if order_line.product_uom != product.uom_id:
                new_price = product.uom_id._compute_quantity(
                    1, order_line.product_uom
                )
            order_line.write({'price_unit': new_price})

    def _sync_sale_quote_lines(self, product):
        sale_quote_lines = self.env['sale.quote.line'].search(
            [
                ('product_id', '=', product.id),
            ]
        )
        for quote_line in sale_quote_lines:
            new_price = product.lst_price
            if quote_line.product_uom_id != product.uom_id:
                new_price = product.uom_id._compute_quantity(
                    1, quote_line.product_uom_id
                )
            quote_line.write({'price_unit': new_price})

    def _sync_sale_quote_options(self, product):
        sale_quote_options = self.env['sale.quote.option'].search(
            [
                ('product_id', '=', product.id),
            ]
        )
        for quote_option in sale_quote_options:
            new_price = product.lst_price
            if quote_option.uom_id != product.uom_id:
                new_price = product.uom_id._compute_quantity(
                    1, quote_option.uom_id
                )
            quote_option.write({'price_unit': new_price})

    @api.multi
    def execute(self):
        self.ensure_one()
        for product in self.product_ids:
            if self.sync_sale_order_line:
                self._sync_sale_order_lines(product=product)
            if self.sync_sale_quote_line:
                self._sync_sale_quote_lines(product=product)
            if self.sync_sale_quote_option:
                self._sync_sale_quote_options(product=product)
