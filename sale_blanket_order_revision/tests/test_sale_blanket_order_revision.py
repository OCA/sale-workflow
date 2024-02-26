from datetime import timedelta

from odoo import fields
from odoo.tests import Form

from odoo.addons.base_revision.tests import test_base_revision


class TestSaleOrderRevision(test_base_revision.TestBaseRevision):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.revision_model = cls.env["sale.blanket.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product = cls.env["product.product"].create({"name": "Test product"})

    def _create_tester(self):
        sale_form = Form(self.revision_model)
        sale_form.partner_id = self.partner
        sale_form.validity_date = fields.Date.today() + timedelta(days=30)
        with sale_form.line_ids.new() as line_form:
            line_form.product_id = self.product
        return sale_form.save()
