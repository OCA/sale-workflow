# Copyright 2022 Camptocamp SA (<https://www.camptocamp.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form

from odoo.addons.base_revision.tests import test_base_revision


class TestSaleOrderRevision(test_base_revision.TestBaseRevision):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.revision_model = cls.env["sale.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product = cls.env["product.product"].create({"name": "Test product"})

    def _create_tester(self):
        sale_form = Form(self.revision_model)
        sale_form.partner_id = self.partner
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
        return sale_form.save()

    def test_revision_preserve_state(self):
        """New revision create does not change state of original SO."""
        # We create an SO and a revision
        tester_1 = self._create_tester()
        self.assertTrue(tester_1.active)

        tester_1.create_revision()
        # we have a revision
        self.assertEqual(len(tester_1.current_revision_id), 1)
        # After the revision creation it is still active
        self.assertTrue(tester_1.active)

    def test_revision_confirm(self):
        """When we confirm one of the revisions, all other are canceled"""

        # We create an SO and 2 revisions
        # They are all active and in state draft
        tester_1 = self._create_tester()
        tester_1.create_revision()
        revision_1 = tester_1.current_revision_id
        revision_1.create_revision()
        revision_2 = revision_1.current_revision_id
        self.assertTrue(tester_1.active)
        self.assertTrue(revision_1.active)
        self.assertTrue(revision_2.active)
        self.assertEqual(tester_1.state, "draft")
        self.assertEqual(revision_1.state, "draft")
        self.assertEqual(revision_2.state, "draft")

        revision_1.action_confirm()
        # One is valid and the other two linked SO are canceled
        self.assertEqual(tester_1.state, "cancel")
        self.assertEqual(revision_1.state, "sale")
        self.assertEqual(revision_2.state, "cancel")

    def test_revision(self):
        """Check revision process"""
        # Create a Tester document
        tester_1 = self._create_tester()

        # Create a revision of the Tester
        tester_1.create_revision()

        # Check the previous revision of the tester
        revision_1 = tester_1.current_revision_id
        self.assertEqual(tester_1.state, "draft")

        # Check the current revision of the tester
        self.assertEqual(revision_1.unrevisioned_name, tester_1.name)
        self.assertEqual(revision_1.state, "draft")
        self.assertTrue(revision_1.active)
        self.assertEqual(revision_1.old_revision_ids, tester_1)
        self.assertEqual(revision_1.revision_number, 1)
        self.assertEqual(revision_1.name.endswith("-01"), True)
        self.assertEqual(revision_1.has_old_revisions, True)
        self.assertEqual(revision_1.revision_count, 1)

        # Create a new revision of the tester
        revision_1.create_revision()
        revision_2 = revision_1.current_revision_id

        # Check the previous revision of the tester
        self.assertEqual(revision_1.state, "draft")
        self.assertTrue(revision_1.active)
        # Check the current revision of the tester
        self.assertEqual(revision_2.unrevisioned_name, tester_1.name)
        self.assertEqual(revision_2, tester_1.current_revision_id)
        self.assertEqual(revision_2.state, "draft")
        self.assertTrue(revision_2.active)
        self.assertEqual(revision_2.old_revision_ids, tester_1 + revision_1)
        self.assertEqual(revision_2.revision_number, 2)
        self.assertEqual(revision_2.name.endswith("-02"), True)
        self.assertEqual(revision_2.has_old_revisions, True)
        self.assertEqual(revision_2.revision_count, 2)

    def test_simple_copy(self):
        """Check copy process"""
        # Create a tester
        tester_2 = self._create_tester()
        # Check the 'Order Reference' of the tester
        self.assertEqual(tester_2.name, tester_2.unrevisioned_name)

        # Copy the tester
        tester_3 = tester_2.copy({"name": "TEST0002"})
        # Check the 'Reference' of the copied tester
        self.assertEqual(tester_3.name, tester_3.unrevisioned_name)

    def test_next_rev_number(self):
        """Check we get the next rev number"""
        # Create a Tester document
        tester_1 = self._create_tester()
        next_rev = tester_1._get_next_rev_number()
        self.assertEqual(next_rev, 1)
        tester_1.create_revision()

        # Check the previous revision of the tester
        revision_1 = tester_1.current_revision_id
        next_rev = revision_1._get_next_rev_number()
        self.assertEqual(next_rev, 2)

        # Create a new revision of the tester
        revision_1.create_revision()
