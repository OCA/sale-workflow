# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWorkflowCopyFallback(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env["sale.workflow.process"].search([]).write({"auto_assign": False})
        cls.partner = cls.env["res.partner"].create({"name": "Copy Partner"})
        cls.manual_workflow = cls.env["sale.workflow.process"].create(
            {"name": "Manual workflow", "auto_assign": False}
        )
        cls.auto_workflow = cls.env["sale.workflow.process"].create(
            {
                "name": "Auto workflow",
                "auto_assign": True,
                "auto_assign_domain": "[('partner_id', '=', %d)]" % cls.partner.id,
            }
        )
        product = cls.env["product.product"].create(
            {"name": "Copy Product", "list_price": 5.0, "type": "consu"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "workflow_process_id": cls.manual_workflow.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "price_unit": product.list_price,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

    def _set_mode(self, mode):
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_automatic_workflow.sale_workflow_copy_mode", mode
        )

    def test_fallback_uses_auto_assign_when_it_matches(self):
        # copy_fallback: auto-assign runs first. The matching auto workflow wins over
        # the origin's manual workflow.
        self._set_mode("copy_fallback")
        new_order = self.order.copy()
        self.assertEqual(new_order.workflow_process_id, self.auto_workflow)

    def test_fallback_copies_origin_when_auto_assign_finds_none(self):
        # copy_fallback: no auto workflow matches -> fall back to the origin workflow.
        self.auto_workflow.auto_assign = False
        self._set_mode("copy_fallback")
        new_order = self.order.copy()
        self.assertEqual(new_order.workflow_process_id, self.manual_workflow)

    def test_copy_always_uses_origin_without_re_derive(self):
        # copy: origin workflow copied verbatim, auto-assign is not re-run even though
        # the auto workflow would match.
        self._set_mode("copy")
        new_order = self.order.copy()
        self.assertEqual(new_order.workflow_process_id, self.manual_workflow)

    def test_no_copy_re_derives_only(self):
        self._set_mode("no_copy")
        new_order = self.order.copy()
        self.assertEqual(new_order.workflow_process_id, self.auto_workflow)
