# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2020 Openindustry.it
#   (https://openindustry.it)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends(
        "order_id.state",
        "move_ids.state",
        "move_ids.product_uom_qty",
        "product_uom_qty",
        "product_uom",
    )
    def _compute_qty_to_deliver(self):
        for line in self:
            total = 0.0
            for move in line.move_ids.filtered(
                lambda m: m.state not in ("cancel", "done")
            ):
                if move.product_uom != line.product_uom:
                    total += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom)
                else:
                    total += move.product_uom_qty
            line.qty_to_deliver = total

    qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver',
                                  digits=dp.get_precision(
                                      'Product Unit of Measure'),
                                  copy=False,
                                  string="Qty to Deliver",
                                  store=True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_qty_to_deliver(self):
        for so in self:
            so.qty_to_deliver = sum(so.mapped('order_line.qty_to_deliver'))

    @api.model
    def _search_qty_to_deliver(self, operator, value):
        so_line_obj = self.env['sale.order.line']
        res = []
        so_lines = so_line_obj.search(
            [('qty_to_deliver', operator, value)])
        order_ids = so_lines.mapped('order_id')
        res.append(('id', 'in', order_ids.ids))
        return [('order_line.qty_to_deliver', operator, value)]

    qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver',
                                  search='_search_qty_to_deliver',
                                  string="Qty to Deliver",
                                  default=0.0)
