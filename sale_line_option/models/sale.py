# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    base_price_unit = fields.Float(string='Base Price Unit')
    pricelist_id = fields.Many2one(
        related="order_id.pricelist_id", readonly=True)
    option_ids = fields.One2many(
        comodel_name='sale.order.line.option',
        inverse_name='sale_line_id', string='Options', copy=True,
        help="Options can be defined with product bom")
    display_option = fields.Boolean(
        help="Technical: allow conditional options field display")

    @api.model
    def create(self, vals):
        if 'product_id' in vals:
            product = self.env['product.product'].browse(vals['product_id'])
            price_unit = vals.get('price_unit', 0.0)
            vals.update(self._set_product(product, price_unit))
        return super(SaleOrderLine, self).create(vals)

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.option_ids = False
            values = self._set_product(self.product_id, self.price_unit)
            for field in values:
                self[field] = values[field]
        return res

    @api.model
    def _set_product(self, product, price_unit):
        """ Shared code between onchange and create/write methods """
        implied = {}
        implied['display_option'], implied['option_ids'] = \
            self._set_option_lines(product)
        implied['base_price_unit'] = price_unit
        return implied

    @api.model
    def _set_option_lines(self, product):
        lines = []
        display_option = False
        bline = None
        bom_lines = self.env['mrp.bom.line'].with_context(
            filter_bom_with_product=product).search([])
        for bline in bom_lines:
            if bline.option_qty:
                vals = {'bom_line_id': bline.id,
                        'product_id': bline.product_id.id,
                        'qty': bline.option_qty}
                lines.append((0, 0, vals))  # create
        if bline:
            display_option = True
        return (display_option, lines)

    @api.onchange('option_ids', 'base_price_unit')
    def _onchange_option(self):
        final_options_price = 0
        for option in self.option_ids:
            final_options_price += option.line_price
            self.price_unit = final_options_price + self.base_price_unit


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_vals_lot_number(self, order_line, index_lot):
        res = super(SaleOrder, self)._prepare_vals_lot_number(
            order_line, index_lot)
        res['option_ids'] = [
            (6, 0, [line.id for line in order_line.option_ids])
        ]
        return res


class SaleOrderLineOption(models.Model):
    _name = 'sale.order.line.option'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        required=True,
        ondelete='cascade')
    bom_line_id = fields.Many2one(
        comodel_name='mrp.bom.line', string='Bom Line', ondelete="set null")
    product_ids = fields.Many2many(
        comodel_name='product.product', compute='_compute_opt_products')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    qty = fields.Integer(default=1)
    opt_max_qty = fields.Integer(related='bom_line_id.opt_max_qty')
    invalid_qty = fields.Boolean(
        compute='_compute_invalid_qty',
        store=True)
    line_price = fields.Float(compute='_compute_price', store=True)

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderLineOption, self).default_get(fields)
        line_product_id = self.env.context.get('line_product_id')
        if line_product_id:
            bom_lines = self.env['mrp.bom.line'].with_context(
                filter_bom_with_product=line_product_id).search([])
            res['product_ids'] = [x.product_id.id for x in bom_lines]
        return res

    @api.onchange('product_id')
    def _onchange_product(self):
        """ we need to store bom_line_id to compute option price """
        line_product_id = self.env.context.get('line_product_id')
        bom_line = self.env['mrp.bom.line'].with_context(
            filter_bom_with_product=line_product_id).search([
                ('product_id', '=', self.product_id.id)], limit=1)
        self.bom_line_id = bom_line and bom_line.id

    def _compute_opt_products(self):
        """ required to set available options """
        prd_ids = [x.product_id.id
                   for x in self[0].bom_line_id.bom_id.bom_line_ids]
        for rec in self:
            rec.product_ids = prd_ids

    def _get_bom_line_price(self):
        self.ensure_one()
        ctx = {'uom': self.bom_line_id.product_uom_id.id}
        if self.sale_line_id.order_id.date_order:
            ctx['date'] = self.sale_line_id.order_id.date_order
        pricelist = self.sale_line_id.pricelist_id.with_context(ctx)
        price = pricelist.price_get(
            self.product_id.id,
            self.bom_line_id.product_qty or 1.0,
            self.sale_line_id.order_id.partner_id.id)
        return price[pricelist.id] * self.bom_line_id.product_qty * self.qty

    @api.depends('qty', 'product_id')
    def _compute_price(self):
        for record in self:
            if record.product_id and record.sale_line_id.pricelist_id:
                record.line_price = record._get_bom_line_price()
            else:
                record.line_price = 0

    @api.multi
    @api.depends('qty')
    def _compute_invalid_qty(self):
        for record in self:
            if record.bom_line_id and \
                    record.qty > record.opt_max_qty:
                record.invalid_qty = True
            else:
                record.invalid_qty = False

    @api.multi
    @api.onchange('qty')
    def onchange_qty(self):
        for record in self:
            if self.bom_line_id and record.opt_max_qty < record.qty:
                return {'warning': {
                    'title': _('Error on quantity'),
                    'message': _(
                        "Maximal quantity of this option is %(max)s.\n"
                        "You encoded %(qty)s.") % {
                            'qty': record.qty,
                            'max': record.opt_max_qty}
                    }
                }
