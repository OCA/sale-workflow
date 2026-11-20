# Copyright 2017 Acsone SA/NV (http://www.acsone.eu)
# Copyright 2026 Studio73 - Pablo Cortés <pablo.cortes@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class SaleInvoicePolicyCommon(BaseCommon):
    _test_user_groups = (
        "base.group_user",
        "sales_team.group_sale_salesman",
        "stock.group_stock_user",
        "account.group_account_invoice",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Goods ordered policy",
                "type": "consu",
                "list_price": 20.0,
                "invoice_policy": "order",
                "taxes_id": [Command.clear()],
            }
        )
        cls.product_delivery = cls.env["product.product"].create(
            {
                "name": "Goods delivered policy",
                "type": "consu",
                "list_price": 45.0,
                "invoice_policy": "delivery",
                "taxes_id": [Command.clear()],
            }
        )
        cls.service = cls.env["product.product"].create(
            {
                "name": "Service ordered policy",
                "type": "service",
                "list_price": 20.0,
                "invoice_policy": "order",
                "taxes_id": [Command.clear()],
            }
        )
        cls.product_ordered_price = cls.env["product.product"].create(
            {
                "name": "Goods delivered at ordered price",
                "type": "consu",
                "list_price": 20.0,
                "invoice_policy": "delivery",
                "taxes_id": [Command.clear()],
            }
        )
        combo_a = cls.env["product.combo"].create(
            {
                "name": "Combo A",
                "combo_item_ids": [Command.create({"product_id": cls.product.id})],
            }
        )
        combo_b = cls.env["product.combo"].create(
            {
                "name": "Combo B",
                "combo_item_ids": [
                    Command.create({"product_id": cls.product_delivery.id})
                ],
            }
        )
        cls.combo_a = combo_a
        cls.combo_b = combo_b
        cls.product_combo = cls.env["product.product"].create(
            {
                "name": "Combo",
                "type": "combo",
                "list_price": 10.0,
                "taxes_id": [Command.clear()],
                "combo_ids": [Command.link(combo_a.id), Command.link(combo_b.id)],
            }
        )
        redirect_form = cls.env["ir.ui.view"].create(
            {
                "name": "Dummy Redirect Form",
                "type": "qweb",
                "arch": "<form action='dummy' method='post'/>",
            }
        )
        cls.provider = cls.env["payment.provider"].create(
            {
                "name": "Test provider",
                "code": "none",
                "is_published": True,
                "redirect_form_view_id": redirect_form.id,
            }
        )
        cls.payment_method = cls.env["payment.method"].create(
            {
                "name": "Test method",
                "code": "test_invoice_policy",
                "active": True,
                "provider_id": cls.provider.id,
            }
        )

    def _create_order(self, invoice_policy, lines, **values):
        order_lines = []
        for line in lines:
            order_lines.append(Command.create(line))
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "user_id": self._test_user.id,
                "invoice_policy": invoice_policy,
                "order_line": order_lines,
                **values,
            }
        )

    def _deliver(self, picking, quantity):
        for move in picking.move_ids:
            move.quantity = quantity
            move.picked = True
        result = picking.button_validate()
        if isinstance(result, dict):
            wizard = (
                self.env[result["res_model"]]
                .with_context(**result.get("context", {}))
                .create({})
            )
            wizard.process()
        backorder = self.env["stock.picking"]
        for candidate in picking.backorder_ids:
            backorder = candidate
        return backorder
