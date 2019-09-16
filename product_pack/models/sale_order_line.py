##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Fields for sale order pack
    pack_total = fields.Float(
        compute='_compute_pack_total'
    )
    pack_line_ids = fields.One2many(
        'sale.order.line.pack.line',
        'order_line_id',
        'Pack Lines'
    )
    pack_type = fields.Selection(
        related='product_id.pack_price_type',
        readonly=True,
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
        ondelete="cascade",
        # copy=False,
    )
    pack_child_line_ids = fields.One2many(
        'sale.order.line',
        'pack_parent_line_id',
        'Lines in pack'
    )

    @api.constrains('product_id', 'product_uom_qty')
    def expand_pack_line(self):
        detailed_packs = ['components_price', 'totalice_price', 'fixed_price']
        # if we are using update_pricelist or checking out on ecommerce we
        # only want to update prices
        do_not_expand = self._context.get('update_prices') or \
            self._context.get('update_pricelist', False)
        if (
                self.state == 'draft' and
                self.product_id.pack and
                self.pack_type in detailed_packs):
            for subline in self.product_id.pack_line_ids:
                vals = subline.get_sale_order_line_vals(
                    self, self.order_id)
                vals['sequence'] = self.sequence
                existing_subline = self.search([
                    ('product_id', '=', subline.product_id.id),
                    ('pack_parent_line_id', '=', self.id),
                ], limit=1)
                # if subline already exists we update, if not we create
                if existing_subline:
                    if do_not_expand:
                        vals.pop('product_uom_qty')
                    existing_subline.write(vals)
                elif not do_not_expand:
                    self.create(vals)

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

    @api.depends(
        'pack_line_ids',
        'pack_line_ids.price_subtotal',
    )
    def _compute_pack_total(self):
        for line in self:
            pack_total = 0.0
            if line.pack_line_ids:
                pack_total = sum(x.price_subtotal for x in line.pack_line_ids)
            line.pack_total = pack_total

    @api.onchange('pack_total')
    def _onchange_pack_line_ids(self):
        for line in self:
            line.price_unit = line.pack_total

    @api.constrains('product_id')
    def expand_none_detailed_pack(self):
        if self._context.get('update_pricelist', False):
            return
        if self.product_id.pack_price_type == 'none_detailed_assited_price':
            # remove previus existing lines
            self.pack_line_ids.unlink()

            # create a sale pack line for each product pack line
            for pack_line in self.product_id.pack_line_ids:
                price_unit = pack_line.product_id.lst_price
                quantity = pack_line.quantity
                vals = {
                    'order_line_id': self.id,
                    'product_id': pack_line.product_id.id,
                    'product_uom_qty': quantity,
                    'price_unit': price_unit,
                    'discount': pack_line.discount,
                    'price_subtotal': price_unit * quantity,
                }
                self.pack_line_ids.create(vals)

    def _get_real_price_currency(
            self, product, rule_id, qty, uom, pricelist_id):
        new_list_price, currency_id = super(
            SaleOrderLine, self)._get_real_price_currency(
                product, rule_id, qty, uom, pricelist_id)
        if self.pack_parent_line_id and\
            self.pack_parent_line_id.product_id.pack_price_type in [
                'fixed_price', 'totalice_price']:
            new_list_price = 0.0
        return new_list_price, currency_id

    @api.onchange('product_id', 'product_uom_qty', 'product_uom', 'price_unit',
                  'discount', 'name', 'tax_id')
    def check_pack_line_modify(self):
        """ Do not let to edit a sale order line if this one belongs to pack
        """
        if self._origin.pack_parent_line_id and \
           self._origin.pack_parent_line_id.product_id.allow_modify_pack \
           not in ['only_backend', 'frontend_backend']:
            raise UserError(_(
                'You can not change this line because is part of a pack'
                ' included in this order'))

    @api.multi
    def _get_display_price(self, product):
        # We do this to clean the price if the parent of the
        # component it's that type
        if self.pack_parent_line_id.product_id.pack_price_type in [
                'fixed_price', 'totalice_price']:
            return 0.0
        return super(SaleOrderLine, self)._get_display_price(product)
