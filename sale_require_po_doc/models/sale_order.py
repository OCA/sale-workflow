# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_need_po = fields.Boolean(
        related="partner_id.customer_need_po",
        string="Customer Requires PO",
        readonly=True,
    )
    sale_doc = fields.Text(
        related="partner_id.sale_doc",
        string="Sales Require Documentation",
        readonly=True,
    )
    sale_document_option = fields.Selection(
        [
            ("no_need", "No documentation needed for this Sale"),
            ("done", "Documentation required obtained and archived"),
        ],
        string="Sale Documentation",
    )
    sale_document_note = fields.Text(string="Sale Documentation Notes")

    def action_confirm(self):
        for order in self:
            if order.customer_need_po and not order.client_order_ref:
                raise ValidationError(
                    _(
                        """You can not confirm sale order without \
                    Customer reference."""
                    )
                )
            if order.sale_doc and not order.sale_document_option:
                raise ValidationError(
                    _(
                        """You can not confirm sale order without \
                    Sale Documentation."""
                    )
                )
        return super(SaleOrder, self).action_confirm()
