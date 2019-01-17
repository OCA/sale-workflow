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
            if self.env.context.get('install_mode'):
                # onchange are not played in install mode
                vals = self.play_onchanges(
                    vals, ['product_id', 'product_uom_qty'])
            price_unit = vals.get('price_unit', 0.0)
            vals.update(self._set_product(product, price_unit))
        return super(SaleOrderLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'option_ids' in vals:
            option_ids_val = vals['option_ids']
            # to fix issue of nesteed many2one we replace [5], [4] option of
            # one2many fileds by [6] option (same as : https://github.com/odoo/odoo/issues/17618)
            if option_ids_val and option_ids_val[0][0] == 5 and\
                    len(option_ids_val) > 1 and option_ids_val[1][0] == 4:
                opt_keep_ids = []
                for opt_v in option_ids_val[1:]:
                    if opt_v[0] == 4:
                        opt_keep_ids.append(opt_v[1])
                vals['option_ids'] = [(6, 0, opt_keep_ids)]
        return super(SaleOrderLine, self).write(vals)

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.option_ids = False
            values = self._set_product(self.product_id, self.price_unit)
            for field in values:
                self[field] = values[field]
        return res

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
            if bline.product_qty:
                vals = {'bom_line_id': bline.id,
                        'product_id': bline.product_id.id,
                        'qty': bline.product_qty}
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
        comodel_name='mrp.bom.line', string='Bom Line', ondelete="set null")
    product_ids = fields.Many2many(
        comodel_name='product.product', compute='_compute_opt_products')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    qty = fields.Integer(default=1)
    opt_max_qty = fields.Integer(
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
    def default_get(self, fields):
        res = super(SaleOrderLineOption, self).default_get(fields)
        line_product_id = self.env.context.get('line_product_id')
        if line_product_id:
            bom_lines = self.env['mrp.bom.line'].with_context(
                filter_bom_with_product=line_product_id).search([])
            res['product_ids'] = [x.product_id.id for x in bom_lines]
        return res

    @api.model
    def create(self, vals):
        res = super(SaleOrderLineOption, self).create(vals)
        res.sale_line_id._onchange_option()
        return res

    @api.onchange('product_id')
    def _onchange_product(self):
        """ we need to store bom_line_id to compute option price """
        ctx = {'filter_bom_with_product': self.env.context.get(
            'line_product_id')}
        bom_line = self.env['mrp.bom.line'].with_context(ctx).search([
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

    @api.depends('qty')
    def _compute_invalid_qty(self):
        for record in self:
            if record.bom_line_id and \
                    record.qty > record.opt_max_qty:
                record.invalid_qty = True
            else:
                record.invalid_qty = False

    @api.onchange('qty')
    def onchange_qty(self):
        for record in self:
            if record.bom_line_id and record.opt_max_qty < record.qty:
                max_val = record.qty
                record.qty = record.opt_max_qty
                return {'warning': {
                    'title': _('Error on quantity'),
                    'message': _(
                        "Maximal quantity of this option is %(max)s.\n"
                        "You encoded %(qty)s.\n"
                        "Quantity is set max value") % {
                            'qty': max_val,
                            'max': record.opt_max_qty}
                    }
                }
