# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# © 2017 David BEAL @ Akretion
# © 2019 Mourad EL HADJ MIMOUNE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        res = super(SaleOrder, self).onchange(
            values, field_name, field_onchange)
        idx = 0
        # hack for issue : https://github.com/odoo/odoo/issues/17618
        # Restore options that have been dropped
        if 'order_line' in res['value']:
            for data in res['value']['order_line']:
                if data == (5,):
                    continue
                act, _, line = data
                if act in [0, 1] and 'option_ids' in line:
                    original_line = values['order_line'][idx][2]
                    if original_line:
                        line['option_ids'] = original_line['option_ids']
                idx += 1
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pricelist_id = fields.Many2one(
        related="order_id.pricelist_id", readonly=True)
    option_ids = fields.One2many(
        comodel_name='sale.order.line.option',
        inverse_name='sale_line_id', string='Options', copy=True,
        help="Options can be defined with product bom")
    bom_with_option = fields.Boolean(
        related='product_id.bom_with_option',
        help="Technical: allow conditional options field display",
        store=True)

    @api.multi
    def write(self, vals):
        if vals.get('option_ids'):
            # to fix issue of nesteed many2one we replace [5], [4] option of
            # one2many fileds by [6] option (same as : https://github.com/odoo/odoo/issues/17618)
            if vals['option_ids'][0][0] == 5:
                ids = []
                for opt_v in vals['option_ids'][1:]:
                    if opt_v[0] == 4:
                        ids.append(opt_v[1])
                vals['option_ids'] = [(6, 0, ids)]
        return super(SaleOrderLine, self).write(vals)

    def _prepare_sale_line_option(self, bline):
        return {
            'bom_line_id': bline.id,
            'product_id': bline.product_id.id,
            'qty': bline.opt_default_qty,
            }

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        self.option_ids = False
        if self.product_id.bom_with_option:
            options = []
            bom_lines = self.env['mrp.bom.line'].with_context(
                filter_bom_with_product=self.product_id).search([])
            for bline in bom_lines:
                if bline.opt_default_qty:
                    options.append(
                        (0, 0, self._prepare_sale_line_option(bline)))
            self.option_ids = options
        return res

    @api.onchange('option_ids')
    def _onchange_option(self):
        self.price_unit = sum(self.option_ids.mapped('line_price'))

    @api.model
    def _prepare_vals_lot_number(self, index_lot):
        res = super(SaleOrderLine, self)._prepare_vals_lot_number(index_lot)
        res['option_ids'] = [
            (6, 0, [line.id for line in self.option_ids])
        ]
        return res


class SaleOrderLineOption(models.Model):
    _name = 'sale.order.line.option'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        required=True,
        ondelete='cascade')
    bom_line_id = fields.Many2one(
        comodel_name='mrp.bom.line',
        string='Bom Line',
        ondelete="set null",
        compute="_compute_bom_line_id",
        store=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    qty = fields.Integer(default=lambda x: x.default_qty)
    min_qty = fields.Integer(
        related='bom_line_id.opt_min_qty', readonly=True)
    default_qty = fields.Integer(
        related='bom_line_id.opt_default_qty', readonly=True)
    max_qty = fields.Integer(
        related='bom_line_id.opt_max_qty', readonly=True)
    invalid_qty = fields.Boolean(
        compute='_compute_invalid_qty', store=True,
        help="Can be used to prevent confirmed sale order")
    line_price = fields.Float(compute='_compute_price', store=True)

    _sql_constraints = [
        ('option_unique_per_line',
         'unique(sale_line_id, product_id)',
         'Option must be unique per Sale line. Check option lines'),
    ]

    @api.model
    def create(self, vals):
        res = super(SaleOrderLineOption, self).create(vals)
        res.sale_line_id._onchange_option()
        return res

    @api.depends('product_id')
    def _compute_bom_line_id(self):
        for record in self:
            ctx = {'filter_bom_with_product': self.env.context.get(
                'line_product_id')}
            bom_line = self.env['mrp.bom.line'].with_context(ctx).search([
                ('product_id', '=', record.product_id.id)], limit=1)
            record.bom_line_id = bom_line and bom_line.id

    def _get_bom_line_price(self):
        self.ensure_one()
        ctx = {'uom': self.bom_line_id.product_uom_id.id}
        if self.sale_line_id.order_id.date_order:
            ctx['date'] = self.sale_line_id.order_id.date_order
        pricelist = self.sale_line_id.pricelist_id.with_context(ctx)
        price = pricelist.price_get(
            self.product_id.id,
            self.qty,
            self.sale_line_id.order_id.partner_id.id)
        return price[pricelist.id] * self.qty

    @api.depends('qty', 'product_id')
    def _compute_price(self):
        for record in self:
            if record.product_id and record.sale_line_id.pricelist_id:
                record.line_price = record._get_bom_line_price()
            else:
                record.line_price = 0

    def _is_quantity_valid(self, record):
        """Ensure product_qty <= qty <= max_qty."""
        if not record.bom_line_id:
            return True
        if record.qty < record.bom_line_id.opt_min_qty:
            return False
        if record.qty > record.bom_line_id.opt_max_qty:
            return False
        return True

    @api.depends('qty')
    def _compute_invalid_qty(self):
        for record in self:
            record.invalid_qty = not record._is_quantity_valid(record)

    @api.onchange('qty')
    def onchange_qty(self):
        for record in self:
            if not self._is_quantity_valid(record):
                # Wrong message if qty is inferior
                max_val = record.qty
                record.qty = record.max_qty
                return {'warning': {
                    'title': _('Error on quantity'),
                    'message': _(
                        "Maximal quantity of this option is %(max)s.\n"
                        "You encoded %(qty)s.\n"
                        "Quantity is set max value") % {
                            'qty': max_val,
                            'max': record.max_qty}
                    }
                }
