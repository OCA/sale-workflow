# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
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
    request_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancel')],
        related='request_id.state',
        string='Request state'
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
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
            self.update({
                'product_uom_id': self.product_id.uom_id,
                'description': (
                    sol_obj.get_sale_order_line_multiline_description_sale(
                        self.product_id)),
            })

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
