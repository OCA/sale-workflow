# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

import time
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT_FORMAT
import odoo.addons.decimal_precision as dp


class SaleProcurementWizard(models.TransientModel):
    _name = 'sale.procurement.wizard'
    _description = 'Procure the returned quantity'

    @api.returns('rma.order.line')
    def _prepare_item(self, line):
        values = {'product_id': line.product_id.id,
                  'product_qty': line.product_qty - line.qty_delivered +
                  line.returned_qty,
                  'uom_id': line.product_uom.id,
                  'line_id': line.id,
                  'order_id': line.order_id and line.order_id.id or False,
                  'wiz_id': self.env.context['active_id'],
                  }
        return values

    @api.model
    def default_get(self, fields):
        """Default values for wizard, if there is more than one supplier on
        lines the supplier field is empty otherwise is the unique line
        supplier.
        """
        context = self._context.copy()
        res = super(SaleProcurementWizard, self).default_get(fields)
        sale_obj = self.env['sale.order']
        sale_ids = self.env.context['active_ids'] or []
        active_model = self.env.context['active_model']

        if not sale_ids:
            return res
        assert active_model == 'sale.order', \
            'Bad context propagation'

        items = []
        order = sale_obj.browse(sale_ids)
        if len(order) > 1:
            raise ValidationError(
                _('Only one order at a time'))
        if order.state not in 'sale':
            raise UserError(_("The order is not confirmed."))
        for line in order.order_line:
            items.append([0, 0, self._prepare_item(line)])
        res['item_ids'] = items
        res['order_id'] = order.id
        context.update({'items_ids': items})
        return res

    item_ids = fields.One2many(
        'sale.procurement.wizard.item',
        'wiz_id', string='Items')
    order_id = fields.Many2one('sale.order',
                               readonly=True)

    @api.multi
    def action_create_picking(self):
        for item in self.item_ids:
            item.with_context(
                manual=True,
                product=item.product_id.id,
                qty=item.product_qty,
                uom=item.uom_id.id).line_id._action_procurement_create()


class SaleProcurementWizardItem(models.TransientModel):
    _name = "sale.procurement.wizard.item"
    _description = "Lines to procure"

    wiz_id = fields.Many2one(
        'sale.procurement.wizard',
        string='Wizard', required=True)
    line_id = fields.Many2one('sale.order.line',
                              string='Sale order Line',
                              readonly=True,
                              ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(
        string='Pending Qty',
        digits=dp.get_precision('Product Unit of Measure'))
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')
