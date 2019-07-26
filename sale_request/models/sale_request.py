# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare
from odoo.exceptions import UserError


class SaleRequest(models.Model):
    _name = 'sale.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sale Request'
    _order = 'date desc, id desc'

    @api.model
    def _company_get(self):
        company_id = self.env['res.company']._company_default_get(self._name)
        return self.env['res.company'].browse(company_id.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env.user

    name = fields.Char(
        required=True,
        readonly=True,
        default="/",
        copy=False,
    )
    date = fields.Datetime(
        required=True,
        default=lambda self: fields.Datetime.now(),
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        domain=[('customer', '=', True)],
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancel')],
        default='draft',
        required=True,
        readonly=True,
        track_visibility='onchange',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=_company_get,
    )
    requested_by = fields.Many2one(
        comodel_name='res.users',
        string='Requested by',
        default=_get_default_requested_by,
        required=True,
        track_visibility='onchange',
        readonly=True,
    )
    description = fields.Text()
    line_ids = fields.One2many(
        comodel_name='sale.request.line',
        inverse_name='request_id',
        string='Lines',
        copy=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        related='line_ids.product_id',
        readonly=False,
        help='Field used to search sale requests by product',
    )
    sale_ids = fields.Many2many(
        comodel_name='sale.order',
        compute='_compute_sale_ids',
        string='Sales',
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)',
         'Reference must be unique per Company!'),
    ]

    @api.multi
    def _compute_sale_ids(self):
        for rec in self:
            rec.sale_ids = self.line_ids.mapped('sale_line_ids.order_id.id')

    @api.multi
    def _subscribe_assigned_user(self, vals):
        self.ensure_one()
        if vals.get('assigned_to'):
            self.message_subscribe(partner_ids=[self.assigned_to.id])

    @api.model
    def _create_sequence(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sale.request') or '/'
        return vals

    @api.model
    def create(self, vals):
        """Add sequence if name is not defined and subscribe to the thread
        the user assigned to the request."""
        vals = self._create_sequence(vals)
        res = super().create(vals)
        res._subscribe_assigned_user(vals)
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for request in self:
            request._subscribe_assigned_user(vals)
        return res

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def button_confirm(self):
        self.write({'state': 'confirm'})
        return True

    @api.multi
    def _check_cancel_allowed(self):
        if any([sale.state == 'sale' for sale in self.line_ids.mapped(
                'sale_line_ids')]):
            raise UserError(
                _('You cannot reject a sale request related to '
                  'confirmed sale orders.'))

    @api.multi
    def button_cancel(self):
        self._check_cancel_allowed()
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_sale_request_lines(self):
        return {
            'name': _('Sale request lines'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.request.line',
            'domain': [('id', 'in', self.line_ids.ids)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
            },
        }

    @api.multi
    def button_sale_orders(self):
        self.ensure_one()
        orders = self.line_ids.mapped('sale_line_ids.order_id')
        return {
            'name': _('Sale Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', orders.ids)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
                'is_master_order': False,
            },
        }


class SaleRequestLine(models.Model):
    _name = 'sale.request.line'
    _description = 'Sale Request Line'

    request_id = fields.Many2one(
        comodel_name='sale.request',
        string='Sale Request',
        copy=False,
        ondelete='cascade',
    )
    request_state = fields.Selection(
        string='Request state', related='request_id.state')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        domain=[('sale_ok', '=', True)],
    )
    description = fields.Text()
    product_qty = fields.Float(
        string="Required Quantity",
        required=True,
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0,
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        required=True,
        domain="[('category_id', '=', category_uom_id)]",
    )
    category_uom_id = fields.Many2one(
        related='product_uom_id.category_id',
    )
    sale_line_ids = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='request_line_id',
        string='Sale Order Lines',
        copy=False,
    )
    remaining_product_qty = fields.Float(
        string="Remaining Quantity",
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_remaining_product_qty',
        store=True,
    )
    state = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done')],
        default='pending',
        readonly=True,
        required=True,
    )

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.sale_line_ids:
                raise UserError(_(
                    'You cannot delete a request line that is already linked '
                    'to a Sale Order'))
        return super().unlink()

    @api.depends('product_qty', 'sale_line_ids')
    @api.multi
    def _compute_remaining_product_qty(self):
        for rec in self:
            total_qty = 0.0
            for line in rec.sale_line_ids:
                total_qty += line.product_uom._compute_quantity(
                    line.product_uom_qty, rec.product_uom_id)
            rec.remaining_product_qty = rec.product_qty - total_qty

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = '[%s] %s' % (
                rec.request_id.name, rec.product_id.display_name)
            res.append((rec.id, name))
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            sol_obj = self.env['sale.order.line']
            self._onchange_product_id_check_availability()

            self.update({
                'product_uom_id': self.product_id.uom_id,
                'description': (
                    sol_obj.get_sale_order_line_multiline_description_sale(
                        self.product_id)),
            })

    @api.onchange('product_id')
    def _onchange_product_id_uom_check_availability(self):
        self._onchange_product_id_check_availability()

    # This is a copy from original method that belong to sale.order.line
    # this method is adapted to sale.request.line model
    @api.onchange('product_qty')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_qty:
            return {}
        if self.user_has_groups('sale_request.group_allow_request_no_stock'):
            return {}
        if self.product_id.type == 'product':
            products = []
            # this method return components of products that have bom
            # type kit
            products_to_check = self._recursive_search_of_components(
                self.product_id.bom_ids, products)
            if products_to_check:
                self._check_availability_kit_bom(products_to_check)
            else:
                self._check_availability_normal_bom(self.product_id)

    def _check_availability_normal_bom(self, product):
        precision = self.env['decimal.precision'].precision_get(
                'Product Unit of Measure')
        product = self.product_id.with_context(
            warehouse=self.request_id.warehouse_id.id,
            lang=self.request_id.partner_id.lang or
            self.env.user.lang or 'en_US'
        )
        product_qty = self.product_id.uom_id._compute_quantity(
            self.product_qty, self.product_id.uom_id)
        if float_compare(
            product.virtual_available,
            product_qty,
            precision_digits=precision
        ) == -1:
            is_available = self._check_routing()
            if not is_available:
                message = (
                    _('You plan to sell %s %s of %s but you only have'
                        '%s %s available in %s warehouse.')
                    % (
                        self.product_qty,
                        self.product_id.uom_id.name,
                        self.product_id.name,
                        product.virtual_available,
                        product.uom_id.name,
                        self.request_id.warehouse_id.name
                    )
                )
                # We check if some products are available in other warehouses.
                if float_compare(
                    product.virtual_available,
                    self.product_id.virtual_available,
                    precision_digits=precision
                ) == -1:
                    message += (
                        _('\nThere are %s %s available across all'
                            'warehouses.\n\n')
                        % (
                            self.product_id.virtual_available,
                            product.uom_id.name)
                    )
                    for warehouse in self.env['stock.warehouse'].search(
                        []
                    ):
                        quantity = self.product_id.with_context(
                            warehouse=warehouse.id).virtual_available
                        if quantity > 0:
                            message += (
                                "%s: %s %s\n"
                                % (
                                    warehouse.name,
                                    quantity,
                                    self.product_id.uom_id.name
                                )
                            )
                # I will use the raise excepcion because do not return
                # a warning message
                raise UserError(_(
                    'Not enough inventory! \n %s') % message)

    def _check_availability_kit_bom(self, products_to_check):
        products_raise = ''
        products_fail = []
        for rec in products_to_check:
            precision = self.env['decimal.precision'].precision_get(
                    'Product Unit of Measure')
            product_id = rec['product_id']
            product = product_id.with_context(
                warehouse=self.request_id.warehouse_id.id,
                lang=self.request_id.partner_id.lang or
                self.env.user.lang or 'en_US'
            )
            rec['stock_demand'] = self.product_qty * rec['product_qty']
            product_qty = product_id.uom_id._compute_quantity(
                rec['stock_demand'], product.uom_id)
            if float_compare(
                product.virtual_available,
                product_qty,
                precision_digits=precision
            ) == -1:
                is_available = self._check_routing()
                if not is_available:
                    products_fail.append(product)
                    products_raise += (
                        _('\nName: %s, Available: %s, Demand: %s')
                        % (product.name, product.virtual_available, rec['stock_demand']))
        if products_fail:
            raise UserError(
                _('You do not have enougth stock of these components:\n %s')
                % products_raise)

    @api.multi
    def _recursive_search_of_components(self, boms, products):
        if boms.type == 'phantom':
            for component in boms.bom_line_ids:
                if component.product_id.bom_ids:
                    parent_ids = self._recursive_search_of_components(
                        component.product_id.bom_ids, products)
                if not component.product_id.bom_ids:
                    if component.product_id.type == 'product':
                        dict_component = {
                            'product_id': component.product_id,
                            'product_qty': component.product_qty,
                        }
                        products.append(dict_component)
            return products

    def _check_routing(self):
        """ Verify the route of the product based on the warehouse
            return True if the product availibility in stock does not need to be verified,
            which is the case in MTO, Cross-Dock or Drop-Shipping
        """
        is_available = False
        product_routes = self.product_id.route_ids + self.product_id.categ_id.total_route_ids

        # Check MTO
        wh_mto_route = self.request_id.warehouse_id.mto_pull_id.route_id
        if wh_mto_route and wh_mto_route <= product_routes:
            is_available = True
        else:
            mto_route = False
            try:
                mto_route = self.env['stock.warehouse']._find_global_route('stock.route_warehouse0_mto', _('Make To Order'))
            except UserError:
                # if route MTO not found in ir_model_data, we treat the product as in MTS
                pass
            if mto_route and mto_route in product_routes:
                is_available = True

        # Check Drop-Shipping
        if not is_available:
            for pull_rule in product_routes.mapped('rule_ids'):
                if pull_rule.picking_type_id.sudo(
                    ).default_location_src_id.usage == 'supplier' and\
                        pull_rule.picking_type_id.sudo(
                            ).default_location_dest_id.usage == 'customer':
                    is_available = True
                    break

        return is_available

    @api.multi
    def button_sale_orders(self):
        self.ensure_one()
        orders = self.sale_line_ids.mapped('order_id')
        return {
            'name': _('Sale Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', orders.ids)],
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
                'is_master_order': False,
            },
        }
