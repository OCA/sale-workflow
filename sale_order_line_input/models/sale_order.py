# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_id = fields.Many2one(
        related='order_id.pricelist_id',
        readonly=True,
    )
    # HACK: Overwrite field because the related fields do not get the default
    # value correctly when user adds a new record.
    company_id = fields.Many2one(
        comodel_name="res.company",
        compute="_compute_company_id",
        inverse=lambda self: self,
        related=False,
        readonly=True,
        store=True,
    )

    @api.depends("order_id")
    def _compute_company_id(self):
        for line in self:
            line.company_id = (
                line.order_id.company_id or self.env.user.company_id
            )

    @api.model
    def create(self, vals):
        if not vals.get('order_id', False):
            sale_order = self.env['sale.order']
            new_so = sale_order.new({
                'partner_id': vals.pop('order_partner_id'),
                'company_id': vals.get("company_id"),
            })
            for onchange_method in new_so._onchange_methods['partner_id']:
                onchange_method(new_so)
            order_data = new_so._convert_to_write(new_so._cache)
            vals['order_id'] = sale_order.create(order_data).id
        return super().create(vals)

    @api.multi
    def action_sale_order_form(self):
        self.ensure_one()
        action = self.env.ref('sale.action_orders')
        form = self.env.ref('sale.view_order_form')
        action = action.read()[0]
        action['views'] = [(form.id, 'form')]
        action['res_id'] = self.order_id.id
        return action
