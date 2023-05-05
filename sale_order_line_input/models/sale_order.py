# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pricelist_id = fields.Many2one(
        related="order_id.pricelist_id",
        readonly=True,
    )
    force_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Forced company",
        compute="_compute_force_company_id",
        readonly=False,
        help="Technical field to force company or get it "
        "from env user if order don't exist.",
    )

    @api.depends("order_id")
    def _compute_force_company_id(self):
        """Related company is not computed already when we click create new line"""
        for line in self:
            line.force_company_id = (
                line.order_id.company_id
                # Is not necessary use browse here
                or self.env.context.get("force_company")
                or self.env.company
            )

    @api.onchange("force_company_id")
    def _onchange_force_company_id(self):
        """Assign company_id because is used in domains as partner,
        product, taxes..."""
        for line in self:
            line.company_id = line.force_company_id

    @api.onchange("order_partner_id")
    def _onchange_order_partner_id(self):
        """Create order to correct compute of taxes"""
        if not self.order_partner_id or self.order_id:
            return
        SaleOrder = self.env["sale.order"]
        new_so = SaleOrder.new(
            {"partner_id": self.order_partner_id, "company_id": self.force_company_id}
        )
        for onchange_method in new_so._onchange_methods["partner_id"]:
            onchange_method(new_so)
        order_vals = new_so._convert_to_write(new_so._cache)
        self.order_id = SaleOrder.create(order_vals)

    def action_sale_order_form(self):
        self.ensure_one()
        return self.order_id.get_formview_action()
