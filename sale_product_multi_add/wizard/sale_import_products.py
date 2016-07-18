# -*- coding: utf-8 -*-
# © 2016 Cédric Pigeon, ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

UNIT = dp.get_precision('Product Unit of Measure')


class SaleImportProducts(models.TransientModel):
    _name = 'sale.import.products'
    _description = 'Sale Import Products'

    quantity = fields.Float(string='Quantity', digits_compute=UNIT,
                            default=1.0)
    products = fields.Many2many(comodel_name='product.product',
                                string="Products")

    @api.multi
    def select_products(self):
        so_obj = self.env['sale.order']
        for wizard in self:
            sale = so_obj.browse(self.env.context.get('active_id', False))

            if sale:
                for product in wizard.products:
                    if wizard.quantity:
                        quantity = wizard.quantity
                    else:
                        quantity = 1
                    sol = self.env['sale.order.line']
                    position = sale.fiscal_position.id
                    date_order = sale.date_order
                    uom = product.uom_po_id

                    onchange_f = sol._model.product_id_change

                    vals = onchange_f(self.env.cr, self.env.uid, [],
                                      sale.pricelist_id.id,
                                      product.id, qty=quantity,
                                      uom=uom.id,
                                      partner_id=sale.partner_id.id,
                                      date_order=date_order,
                                      fiscal_position=position,
                                      context=self.env.context)

                    if 'value' in vals:
                        taxes = vals['value']['tax_id']
                        vals['value'].update({'order_id': sale.id,
                                              'product_id': product.id,
                                              'tax_id': [(6, 0, taxes)]})

                        sol.create(vals['value'])

        return {'type': 'ir.actions.act_window_close', }
