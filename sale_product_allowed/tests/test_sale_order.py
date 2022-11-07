# Copyright 2021 Camptocamp SA
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form

from .common import CommonCase


class TestSaleOrderCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

    def test_create(self):
        self.assertRecordValues(
            self.order,
            [
                {
                    # Default configs
                    "product_allowed_config_ids": (
                        self.order.company_id.default_product_allowed_config_id.ids
                    ),
                }
            ],
        )

    def test_onchange_partner(self):
        form = Form(self.order.browse())
        new_partner = self.partner.copy(
            {
                "name": "New Partner w/ New Conf",
                "product_allowed_list_ids": self.product_list.copy().ids,
            }
        )
        form.partner_id = self.partner
        # initial partner had no specific conf
        self.assertEqual(
            form.product_allowed_config_ids._get_ids(),
            self.env.company.default_product_allowed_config_id.ids,
        )
        form.partner_id = new_partner
        self.assertEqual(
            form.product_allowed_config_ids._get_ids(),
            new_partner.product_allowed_list_ids.ids,
        )

    def test_allowed_products(self):
        form = Form(self.order)
        self.partner.product_allowed_list_ids = self.product_list.ids
        form.partner_id = self.partner
        # Reminder for configuration from product_allowed_list.tests.common:
        # {
        #     "product_template_id": cls.prod1.product_tmpl_id.id,
        #     "product_id": cls.prod1.id,
        # },
        # {
        #     "product_template_id": cls.prod2.product_tmpl_id.id,
        # },
        self.assertEqual(
            sorted(form.allowed_product_ids._get_ids()),
            sorted((self.prod1 + self.prod2.product_tmpl_id.product_variant_ids).ids),
        )
