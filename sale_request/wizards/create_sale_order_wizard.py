# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import datetime


class CreateSaleOrderWizard(models.TransientModel):
    _name = 'create.sale.order.wizard'
    _description = 'Create Sale Orders From Sale Request'

    line_ids = fields.One2many(
        comodel_name='create.sale.order.wizard.line',
        inverse_name='wizard_id',
        string='Proposition Sale Order Lines',
    )
    request_line_id = fields.Many2one(
        comodel_name='sale.request.line',
        string='Sale Request Line',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True,
    )
    product_qty = fields.Float(
        string="Quantity",
        readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        readonly=True,
    )
    remaining_product_qty = fields.Float(
        string="Required Quantity",
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    has_lines = fields.Boolean(
        compute='_compute_has_lines',
    )

    def _calcule_on_time(self):
        time = fields.datetime.now()
        hour_zone = fields.Datetime.context_timestamp(self, time)
        hour = hour_zone.hour
        minute = hour_zone.minute

        # get time start from system parameter
        time_start = self.env.ref(
            'sale_request.sale_request_time_start')
        time_finish = self.env.ref(
            'sale_request.sale_request_time_finish')

        sale_r_time_start = int(
            time_start.value)
        sale_r_time_finish = int(
            time_finish.value)

        # convert time to minutes, that way is more easy
        # use different time hours

        # In this line code we need plus the minutes
        # but in this case the minute also start as finish is 0
        # for that reason i do not added
        start_time = sale_r_time_start*60
        end_time = sale_r_time_finish*60
        current_time = hour*60 + minute
        if start_time <= current_time and end_time >= current_time:
            return True
        return False

    on_time = fields.Boolean(
        default=_calcule_on_time,
    )

    @api.multi
    @api.depends('request_line_id')
    def _compute_has_lines(self):
        for rec in self:
            rec.has_lines = bool(rec.line_ids)

    @api.onchange('line_ids')
    def _onchange_qty_to_sale(self):
        if self.line_ids:
            remaining_product_qty = self.request_line_id.remaining_product_qty
            qty_to_sale = 0.0
            for line in self.line_ids:
                qty_to_sale += line.product_uom_id._compute_quantity(
                    line.qty_to_sale, self.product_uom_id)
            new_remaining_qty = remaining_product_qty - qty_to_sale
            if new_remaining_qty < 0:
                self.remaining_product_qty = remaining_product_qty
                return {
                    'warning': {
                        'title': _('Error!'),
                        'message': _('You cannot request more than the'
                                     ' initial demand of this sale request.'),
                    },
                }
            self.remaining_product_qty = new_remaining_qty

    @api.model
    def _prepare_item(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.name,
            'product_uom_qty': line.product_uom_qty,
            'product_uom_id': line.product_uom.id,
            'order_id': line.order_id.id,
            'client_order_ref': line.order_id.client_order_ref,
            'sale_line_id': line.id,
            'remaining_product_qty': line.remaining_product_qty,
            'qty_to_sale': 0,
        }

    @api.model
    def default_get(self, res_fields):
        res = super().default_get(res_fields)
        rqst_line = self.env['sale.request.line'].browse(
            self._context.get('active_ids'))
        order_lines = self.env['sale.order.line'].search(
            [('state', '=', 'sale'),
             ('product_id', '=', rqst_line.product_id.id),
             ('order_id.master_sale_order', '=', True),
             ('remaining_product_qty', '>', 0.0),
             ('order_id.partner_id', '=', rqst_line.request_id.partner_id.id)])
        wiz_lines = []
        for line in order_lines:
            wiz_lines.append((0, 0, self._prepare_item(line)))
        res.update({
            'request_line_id': rqst_line.id,
            'product_id': rqst_line.product_id.id,
            'product_qty': rqst_line.product_qty,
            'product_uom_id': rqst_line.product_uom_id.id,
            'remaining_product_qty': rqst_line.remaining_product_qty,
            'line_ids': wiz_lines,
        })
        return res

    @api.model
    def _prepare_sale_order(self, request, sale_line_id, pricelist_id):
        client_order_ref = False
        if sale_line_id:
            client_order_ref = sale_line_id.order_id.client_order_ref
        partner = request.partner_id.id
        fpos_id = self.env['account.fiscal.position'].get_fiscal_position(
            partner)
        return {
            'partner_id': request.partner_id.id,
            'user_id': self.env.user.id,
            'company_id': request.company_id.id,
            'date_order': fields.Date.context_today(self),
            'client_order_ref': client_order_ref,
            'origin': request.name,
            'warehouse_id': request.warehouse_id.id,
            'request_id': request.id,
            'fiscal_position_id': fpos_id,
            'pricelist_id': pricelist_id,
        }

    @api.model
    def _get_pricelist_id(self, request_line):
        product = request_line.product_id
        partner = request_line.request_id.partner_id.id
        pricelist_id = False
        if product.item_ids:
            pricelist_id = product.item_ids[0].pricelist_id.id
        if not pricelist_id:
            pricelist_obj = self.env['product.pricelist']
            pricelist_id = pricelist_obj._get_partner_pricelist(
               partner, self.env.user.company_id.id)
        return pricelist_id

    @api.model
    def _get_sale_order(self, request_line, sale_line=False):
        pricelist_id = self._get_pricelist_id(request_line)
        so_obj = self.env['sale.order']
        domain = [
            ('request_id', '=', request_line.request_id.id),
            ('pricelist_id', '=', pricelist_id)]
        if sale_line:
            domain.append(
                ('client_order_ref', '=', sale_line.order_id.client_order_ref))
        order = so_obj.search(domain)
        if not order:
            order = so_obj.create(self._prepare_sale_order(
                request_line.request_id, sale_line, pricelist_id))
        return order

    @api.multi
    def _prepare_sale_order_line(self,  order, params):
        request_line = self.request_line_id
        product = request_line.product_id
        taxes = product.taxes_id
        if order.fiscal_position_id:
            taxes = order.fiscal_position_id.map_tax(taxes, product)
        price = order.pricelist_id.get_product_price(
            product, params['qty_to_sale'], order.partner_id, order.date_order,
            params['product_uom'])
        price_unit = self.env['account.tax']._fix_tax_included_price_company(
            price, taxes, taxes, self.env.user.company_id)
        return {
            'product_id': request_line.product_id.id,
            'product_uom_qty': params['qty_to_sale'],
            'product_uom': params['product_uom'],
            'request_line_id': request_line.id,
            'parent_id': params['sale_line_id'],
            'order_id': order.id,
            'tax_id': [(6, 0, taxes.ids)],
            'price_unit': price_unit,
        }

    @api.multi
    def create_sale_order(self):
        self.ensure_one()
        if not self.on_time:
            self.line_ids = False
        qty_to_sale = 0.0
        for line in self.line_ids:
            qty_to_sale += line.product_uom_id._compute_quantity(
                line.qty_to_sale, self.product_uom_id)
        if qty_to_sale > self.request_line_id.remaining_product_qty:
            raise UserError(
                _('Error! The quantity to sale is greather than'
                    ' the requested quantity.'))
        so_obj = self.env['sale.order']
        sol_obj = self.env['sale.order.line']
        request_line = self.request_line_id.sudo()
        lines = self.line_ids.filtered('qty_to_sale')
        if self.line_ids and not lines:
            raise UserError(
                _('You have not defined the quantity to sale to any master '
                  'order, please define it.'))
        if not self.line_ids:
            sale_line = self.env['sale.order.line'].search([
                ('request_line_id', '=', self.request_line_id.id)])
            if sale_line:
                raise UserError(
                    _('Error! The quantity to sale is greather than'
                        ' the requested quantity.'))
            order = self._get_sale_order(request_line)
            so_obj |= order
            params = {
                'qty_to_sale': request_line.product_qty,
                'product_uom': request_line.product_uom_id.id,
                'sale_line_id': False,
            }
            values = self._prepare_sale_order_line(order, params)
            sol_obj.create(values)
            request_line.remaining_product_qty = 0
        else:
            rqst_remaining_product_qty = request_line.remaining_product_qty
            for line in lines:
                sale_line = line.sale_line_id
                order = self._get_sale_order(request_line, sale_line)
                so_obj |= order
                line_remaining_qty = line.product_uom_id._compute_quantity(
                    sale_line.remaining_product_qty,
                    request_line.product_uom_id)
                if (line_remaining_qty >= rqst_remaining_product_qty):
                    rqst_remaining_product_qty -= (
                        line.product_uom_id._compute_quantity(
                            line.qty_to_sale, request_line.product_uom_id))
                params = {
                    'qty_to_sale': line.qty_to_sale,
                    'product_uom': line.product_uom_id.id,
                    'sale_line_id': line.sale_line_id.id,
                }
                values = self._prepare_sale_order_line(order, params)
                sol_obj.create(values)
        for sale_order in so_obj:
            sale_order.action_confirm()
        if request_line.remaining_product_qty == 0.0:
            request_line.state = 'done'
            request = request_line.request_id
            if not request.line_ids.filtered(
                    lambda l: l.state != 'done'):
                request.state = 'done'
        res = {
            'name': _('Sale Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': order.id,
            'type': 'ir.actions.act_window',
            'context': {
                'create': False,
                'delete': False,
            }
        }
        if len(so_obj) > 1:
            res['view_mode'] = 'tree,form'
            res['domain'] = [('id', 'in', so_obj.ids)]
            del res['res_id']
        return res


class CreateSaleOrderWizardLine(models.TransientModel):
    _name = 'create.sale.order.wizard.line'
    _description = 'Lines to Create Sale Orders From Sale Request'

    wizard_id = fields.Many2one(
        comodel_name='create.sale.order.wizard',
        string='Wizard',
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        readonly=True,
    )
    client_order_ref = fields.Char(string='Customer Purchase Order')
    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Order Line',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        readonly=True,
    )
    name = fields.Text(
        string="Description",
    )
    product_uom_qty = fields.Float(
        string='Ordered Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    remaining_product_qty = fields.Float(
        string='Remaining Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    product_uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        related='sale_line_id.product_uom',
    )
    qty_to_sale = fields.Float(
        string='Quantity to Sale',
        digits=dp.get_precision('Product Unit of Measure'),
    )

    @api.onchange('qty_to_sale')
    def _onchange_qty_to_sale(self):
        if self.qty_to_sale:
            remaining_product_qty = self.sale_line_id.remaining_product_qty
            new_remaining_qty = remaining_product_qty - self.qty_to_sale
            if new_remaining_qty < 0:
                self.remaining_product_qty = remaining_product_qty
                return {
                    'warning': {
                        'title': _('Error!'),
                        'message': _(
                            'You cannot request more than the '
                            'remaining qty of this master sale order.'),
                    },
                }
            self.remaining_product_qty = new_remaining_qty
