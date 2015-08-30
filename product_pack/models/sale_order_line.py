# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import fields, models, api, _


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    # Fields for sale order pack
    pack_total = fields.Float(
        string='Pack total',
        compute='_get_pack_total'
        )
    pack_line_ids = fields.One2many(
        'sale.order.line.pack.line',
        'order_line_id',
        'Pack Lines'
        )
    sale_order_pack = fields.Boolean(
        related='product_id.sale_order_pack'
        )

    # Fields for common packs
    pack_depth = fields.Integer(
        'Depth',
        help='Depth of the product if it is part of a pack.'
    )
    pack_parent_line_id = fields.Many2one(
        'sale.order.line',
        'Pack',
        help='The pack that contains this product.',
        ondelete="cascade"
    )
    pack_child_line_ids = fields.One2many(
        'sale.order.line',
        'pack_parent_line_id',
        'Lines in pack'
    )

    @api.multi
    def update_pack_lines(self):
        pack_lines = self.env['sale.order.line']
        for line in self:
            for subline in line.product_id.pack_line_ids:
                vals = subline.get_sale_order_line_vals(
                    line, line.order_id)
                vals['sequence'] = line.sequence
                existing_subline = line.search([
                    ('product_id', '=', subline.product_id.id),
                    ('pack_parent_line_id', '=', line.id),
                    ], limit=1)
                # if subline already exists we update, if not we create
                if existing_subline:
                    existing_subline.write(vals)
                else:
                    new_line = line.create(vals)
                    if (
                            new_line.state == 'draft' and
                            new_line.product_id.pack and
                            not new_line.product_id.sale_order_pack):
                        pack_lines += new_line
        return pack_lines

    @api.multi
    def button_save_data(self):
        return True

    @api.multi
    def action_pack_detail(self):
        view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'product_pack.view_order_line_form2')
        view = {
            'name': _('Details'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'readonly': True,
            'res_id': self.id,
            'context': self.env.context
        }
        return view

    @api.one
    @api.depends(
        'pack_line_ids',
        'pack_line_ids.price_subtotal',
    )
    def _get_pack_total(self):
        pack_total = 0.0
        if self.pack_line_ids:
            pack_total = sum(x.price_subtotal for x in self.pack_line_ids)
        self.pack_total = pack_total

    @api.one
    @api.onchange('pack_total')
    def _onchange_pack_line_ids(self):
        self.price_unit = self.pack_total

    # onchange para agregar los product en el tipo el pack "sale order pack"
    def product_id_change(
            self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        # warning = {}
        if not product:
            return {'value': {
                'th_weight': 0,
                'product_packaging': False,
                'product_uos_qty': qty},
                'domain': {'product_uom': [], 'product_uos': []}
            }
        product_obj = self.pool.get('product.product')
        product_info = product_obj.browse(cr, uid, product)

        result = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging,
            fiscal_position, flag, context)

        pack_line_ids = [(5, False, False)]
        if product_info.pack_line_ids and product_info.sale_order_pack:
            for pack_line in product_info.pack_line_ids:
                price_unit = pack_line.product_id.lst_price
                quantity = pack_line.quantity
                pack_line_ids.append((0, False, {
                    'product_id': pack_line.product_id.id,
                    'product_uom_qty': quantity,
                    'price_unit': price_unit,
                    'price_subtotal': price_unit * quantity,
                }))
        result['value']['pack_line_ids'] = pack_line_ids
        return result
