# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestCustomerinfoElaboration(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer0 = cls.env["res.partner"].create({"name": "Test partner 0"})
        cls.customer1 = cls.env["res.partner"].create(
            {"name": "Test partner 1", "parent_id": cls.customer0.id}
        )
        cls.customer2 = cls.env["res.partner"].create({"name": "Test partner 2"})
        cls.product = cls.env["product.product"].create({"name": "Product test"})
        cls.product_elab = cls.env["product.product"].create(
            {"name": "Elaboration prod. test", "type": "service"}
        )
        cls.elaboration = cls.env["product.elaboration"].create(
            {"name": "Test elaboration", "product_id": cls.product_elab.id}
        )
        cls.customer_info = cls.env["product.customerinfo"].create(
            {
                "partner_id": cls.customer0.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "elaboration_ids": [(4, cls.elaboration.id)],
                "elaboration_note": "Test elaboration note",
            }
        )

    def _create_sale(self, partner):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = partner
        with so_form.order_line.new() as ol_form:
            ol_form.product_id = self.product
        return so_form.save()

    def test_sale_without_elaboration(self):
        so = self._create_sale(self.customer2)
        line = so.order_line
        self.assertFalse(line.elaboration_ids)
        self.assertFalse(line.elaboration_note)

    def test_sale_direct_customerinfo_with_elaboration(self):
        so = self._create_sale(self.customer0)
        line = so.order_line
        self.assertEqual(line.elaboration_ids, self.elaboration)
        self.assertEqual(line.elaboration_note, "Test elaboration note")

    def test_sale_parent_customerinfo_with_elaboration(self):
        so = self._create_sale(self.customer1)
        line = so.order_line
        self.assertEqual(line.elaboration_ids, self.elaboration)
        self.assertEqual(line.elaboration_note, "Test elaboration note")

    def test_multiple_elaboration_per_customer(self):
        product_elab_2 = self.env["product.product"].create(
            {"name": "Elaboration prod. test 2", "type": "service"}
        )
        elaboration_2 = self.env["product.elaboration"].create(
            {"name": "Test elaboration 2", "product_id": product_elab_2.id}
        )
        self.customer_info.elaboration_ids += elaboration_2
        so = self._create_sale(self.customer0)
        line = so.order_line
        self.assertEqual(line.elaboration_ids, self.elaboration | elaboration_2)
        self.assertEqual(line.elaboration_note, "Test elaboration, Test elaboration 2")

    def test_change_elaboration_other_than_customerinfo(self):
        """Changing the line elaborations to others than the customer info ones
        refreshes the note with the new elaboration names.
        """
        elaboration_2 = self.env["product.elaboration"].create(
            {"name": "Test elaboration 2", "product_id": self.product_elab.id}
        )
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer0
        with so_form.order_line.new() as ol_form:
            ol_form.product_id = self.product
            self.assertEqual(ol_form.elaboration_note, "Test elaboration note")
            ol_form.elaboration_ids.clear()
            ol_form.elaboration_ids.add(elaboration_2)
            self.assertEqual(ol_form.elaboration_note, "Test elaboration 2")
            ol_form.elaboration_ids.clear()
            self.assertFalse(ol_form.elaboration_note)
        so = so_form.save()
        self.assertFalse(so.order_line.elaboration_note)

    def test_customerinfo_elaborations_in_different_order(self):
        """Selecting the customer info elaborations again in another order
        restores the customer info note.
        """
        elaboration_2 = self.env["product.elaboration"].create(
            {"name": "Test elaboration 2", "product_id": self.product_elab.id}
        )
        self.customer_info.elaboration_ids += elaboration_2
        self.customer_info.elaboration_note = "Custom note"
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.customer0
        with so_form.order_line.new() as ol_form:
            ol_form.product_id = self.product
            self.assertEqual(ol_form.elaboration_note, "Custom note")
            ol_form.elaboration_ids.clear()
            ol_form.elaboration_ids.add(elaboration_2)
            ol_form.elaboration_ids.add(self.elaboration)
        so = so_form.save()
        self.assertEqual(so.order_line.elaboration_note, "Custom note")
