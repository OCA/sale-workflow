# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    stock_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Pickings",
        domain="""
            [
                ('sale_id', 'in', sale_order_ids),
                ('state', '=', 'done'),
                ('invoiced', '=', False),
            ]
        """,
    )
    inv_service_products = fields.Boolean(
        string="Invoice Service Products",
        compute="_compute_invoice_service_products",
        readonly=False,
        store=True,
        help="If selected and there is a service type " "product, it will be invoiced.",
    )
    there_are_service_product = fields.Boolean(
        string="There are a Service Product",
        compute="_compute_invoice_service_products",
        store=True,
    )

    @api.depends("stock_picking_ids")
    def _compute_invoice_service_products(self):
        for sel in self:
            res = False
            service_lines = (
                sel.stock_picking_ids.mapped("sale_id")
                .mapped("order_line")
                .filtered(
                    lambda x: x.invoice_status == "to invoice"
                    and x.product_id.type == "service"
                )
            )
            if service_lines:
                res = True
            sel.inv_service_products = res
            sel.there_are_service_product = res

    def _create_invoices(self, sale_orders):
        if self.advance_payment_method == "delivered" and self.stock_picking_ids:
            inv = sale_orders.with_context(
                invoice_service_products=self.inv_service_products
            )._create_invoices_from_pickings(self.stock_picking_ids)
        else:
            inv = super()._create_invoices(sale_orders)
        return inv
