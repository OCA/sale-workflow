# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp


class LinkSaleOrderWizard(models.TransientModel):
    _name = 'link.sale.order.wizard'
    _description = 'Link Sale Orders with Master Sale Order'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        readonly=True,
    )
    line_ids = fields.One2many(
        comodel_name='link.master.sale.order.wizard.line',
        inverse_name='wizard_id',
        string='Sale order lines with no link',
    )
    sale_line_ids = fields.Many2many(
        comodel_name='sale.order.line',
        string='Lines with no link',
    )
    product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Products',
        readonly=True,
    )

    @api.multi
    def _prepare_item(self, line):
        return {
            'sale_line_id': line.id,
            'product_id': line.product_id.id,
            'remaining_product_qty': line.remaining_product_qty,
            'name': line.name,
            'product_uom_qty': line.product_uom_qty,
            'product_uom_id': line.product_uom.id,
        }

    @api.onchange('sale_line_ids')
    def _onchange_sale_line_ids(self):
        for wiz_line in self.line_ids:
            qty = 0
            sale_lines = self.sale_line_ids.filtered(
                lambda l: l.product_id.id == wiz_line.product_id.id)
            for sale_line in sale_lines:
                qty += sale_line.product_uom._compute_quantity(
                    sale_line.product_uom_qty, wiz_line.product_uom_id)
            qty += sum(
                wiz_line.sale_line_id.child_ids.mapped('product_uom_qty'))
            wiz_line.remaining_product_qty = wiz_line.product_uom_qty - qty

    @api.model
    def default_get(self, res_fields):
        res = super().default_get(res_fields)
        order = self.env['sale.order'].browse(
            self._context.get('active_ids'))
        wiz_lines = []
        for line in order.order_line:
            wiz_lines.append((0, 0, self._prepare_item(line)))
        res.update({
            'partner_id': order.partner_id.id,
            'product_ids': [(6, 0, order.order_line.mapped('product_id').ids)],
            'line_ids': wiz_lines
        })
        return res

    @api.multi
    def link_sale_order(self):
        self.ensure_one()
        list_order = []
        for wiz_line in self.line_ids:
            sale_lines = self.sale_line_ids.filtered(
                lambda l: l.product_id.id == wiz_line.product_id.id)
            orders = sale_lines.mapped('order_id')
            list_order.extend(orders.ids)
            for order in orders:
                ref = wiz_line.sale_line_id.order_id.client_order_ref
                if (order.client_order_ref and
                        order.client_order_ref != ref):
                    ref = '%s | %s' % (order.client_order_ref, ref)
                order.client_order_ref = ref
            sale_lines.write({
                'parent_id': wiz_line.sale_line_id.id,
            })
        return {
            'name': _('Sale Order'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', list_order)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
            }
        }


class LinkSaleOrderWizardLine(models.TransientModel):
    _name = 'link.master.sale.order.wizard.line'
    _description = 'Lines of Master Sale Order'

    wizard_id = fields.Many2one(
        comodel_name='link.sale.order.wizard',
        string='Wizard',
        readonly=True,
    )
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Order Line',
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True,
    )
    name = fields.Text(
        string="Description",
        readonly=True,
    )
    product_uom_qty = fields.Float(
        string='Ordered Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    remaining_product_qty = fields.Float(
        string='Remaining Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        readonly=True,
    )

    @api.model
    def _prepare_line(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'product_uom_qty': line.product_uom_qty,
            'product_uom_id': line.product_uom.id,
        }

    @api.model
    def create(self, vals):
        """Method overrided to save the readonly fields values"""
        sale_line_id = self.env['sale.order.line'].browse(
            vals.get('sale_line_id'))
        if sale_line_id:
            vals.update(self._prepare_line(sale_line_id))
        res = super().create(vals)
        return res
