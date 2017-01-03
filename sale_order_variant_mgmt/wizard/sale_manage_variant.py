# -*- coding: utf-8 -*-
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.addons.decimal_precision as dp
from openerp import _, api, models, fields, exceptions


class SaleManageVariant(models.TransientModel):
    _name = 'sale.manage.variant'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string="Template")
    variant_line_ids = fields.Many2many(
        comodel_name='sale.manage.variant.line', string="Variant Lines")
    sale_order_line = fields.Many2many(
        compute="_compute_sale_order_line",
        comodel_name='sale.order.line',
        readonly=True,
        string="Sale Order View"
    )

    @api.multi
    def _compute_sale_order_line(self):
        self.ensure_one()
        self.sale_order_line = self.env['sale.order.line'].search([
            ('order_id', '=', self.env.context['active_id'])
        ])
        
    # HACK: https://github.com/OCA/server-tools/pull/492#issuecomment-237594285
    @api.multi
    def onchange(self, values, field_name, field_onchange):  # pragma: no cover
        if "variant_line_ids" in field_onchange:
            for sub in ("product_id", "disabled", "value_x", "value_y",
                        "product_uom_qty"):
                field_onchange.setdefault("variant_line_ids." + sub, u"")
        return super(SaleManageVariant, self).onchange(
            values, field_name, field_onchange)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        self.variant_line_ids = [(6, 0, [])]
        template = self.product_tmpl_id
        context = self.env.context
        record = self.env[context['active_model']].browse(
            context['active_id'])
        if context['active_model'] == 'sale.order.line':
            sale_order = record.order_id
        else:
            sale_order = record
        num_attrs = len(template.attribute_line_ids)
        if not template or not num_attrs:
            return
        line_x = template.attribute_line_ids[0]
        line_y = False if num_attrs == 1 else template.attribute_line_ids[1]
        lines = []
        for value_x in line_x.value_ids:
            for value_y in line_y and line_y.value_ids or [False]:
                # Filter the corresponding product for that values
                values = value_x
                if value_y:
                    values += value_y
                product = template.product_variant_ids.filtered(
                    lambda x: not(values - x.attribute_value_ids))[:1]
                order_line = sale_order.order_line.filtered(
                    lambda x: x.product_id == product)[:1]
                lines.append((0, 0, {
                    'product_id': product,
                    'disabled': not bool(product),
                    'value_x': value_x,
                    'value_y': value_y,
                    'product_uom_qty': order_line.product_uom_qty,
                }))
        self.variant_line_ids = lines

    @api.multi
    def button_transfer_to_order(self):
        self.ensure_one()
        if not self.product_tmpl_id:
            raise exceptions.Warning(
                _('Please select a product for transfer to order'))
        context = self.env.context
        record = self.env[context['active_model']].browse(context['active_id'])
        if context['active_model'] == 'sale.order.line':
            sale_order = record.order_id
        else:
            sale_order = record
        OrderLine = self.env['sale.order.line']
        lines2unlink = OrderLine
        for line in self.variant_line_ids:
            order_line = sale_order.order_line.filtered(
                lambda x: x.product_id == line.product_id)
            if order_line:
                if not line.product_uom_qty:
                    # Done this way because there's a side effect removing here
                    lines2unlink |= order_line
                else:
                    order_line.product_uom_qty = line.product_uom_qty
            elif line.product_uom_qty:
                order_line = OrderLine.new({
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id,
                    'product_uom_qty': line.product_uom_qty,
                    'order_id': sale_order.id,
                })
                order_line.product_id_change()
                order_line_vals = order_line._convert_to_write(
                    order_line._cache)
                sale_order.order_line.create(order_line_vals)
        lines2unlink.unlink()

    @api.multi
    def button_transfer_to_order_and_new(self):
        self.ensure_one()
        self.button_transfer_to_order()
        view_id = self.env.ref(
            'sale_order_variant_mgmt.sale_manage_variant_form')
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.manage.variant',
            'res_id': self.id,
            'view_id': view_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
    
    @api.multi
    def cancel(self):
        self.ensure_one()
        self.sale_order_line.unlink()


class SaleManageVariantLine(models.TransientModel):
    _name = 'sale.manage.variant.line'

    product_id = fields.Many2one(
        comodel_name='product.product', string="Variant", readonly=True)
    disabled = fields.Boolean()
    value_x = fields.Many2one(comodel_name='product.attribute.value')
    value_y = fields.Many2one(comodel_name='product.attribute.value')
    product_uom_qty = fields.Float(
        string="Quantity", digits_compute=dp.get_precision('Product UoS'))
