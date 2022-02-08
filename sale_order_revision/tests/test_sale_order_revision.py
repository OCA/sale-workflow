# Copyright 2021 Tecnativa - Víctor Martínez
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
