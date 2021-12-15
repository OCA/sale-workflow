from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged("post_install", "-at_install")
class TestSaleOrderPartnerRestrict(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.main_company = cls.env.ref("base.main_company")
        cls.second_company = cls.env["res.company"].create({"name": "Second Company"})

        cls.partner_model = cls.env["res.partner"]

        cls.partner_parent = cls.partner_model.create(
            {"name": "Partner Parent", "type": "contact"}
        )
        cls.partner_child = cls.partner_model.create(
            {
                "name": "Partner Child",
                "type": "contact",
                "parent_id": cls.partner_parent.id,
            }
        )
        cls.partner_diff_company = cls.partner_model.create(
            {
                "name": "Partner Different Company",
                "type": "contact",
                "company_id": cls.second_company.id,
            }
        )
        cls.partner_delivery = cls.partner_model.create(
            {
                "name": "Partner Delivery",
                "type": "other",
                "parent_id": cls.partner_parent.id,
            }
        )

    def _create_sale_order(self):
        so = self.env["sale.order"].create({"partner_id": self.partner_parent.id})
        return so

    def test_sale_order_partner_restrict_option_all(self):
        self.main_company.sale_order_partner_restrict = "all"
        self.sale_order_option_all = self._create_sale_order()

        self.assertIn(
            self.partner_parent,
            self.sale_order_option_all.available_partners,
            "Parent and contact type partner should be available on 'all' option",
        )
        self.assertIn(
            self.partner_child,
            self.sale_order_option_all.available_partners,
            "Child and contact type partner should be available in 'all' option",
        )
        self.assertNotIn(
            self.partner_diff_company,
            self.sale_order_option_all.available_partners,
            "Partner from another company"
            " shouldn't be available on this company (option 'all')",
        )
        self.assertIn(
            self.partner_delivery,
            self.sale_order_option_all.available_partners,
            "Child and other type partner should be available in 'all' option",
        )

    def test_sale_order_partner_restrict_option_only_parents(self):
        self.main_company.sale_order_partner_restrict = "only_parents"
        self.sale_order_option_only_parents = self._create_sale_order()

        self.assertIn(
            self.partner_parent,
            self.sale_order_option_only_parents.available_partners,
            "Parent and contact type partner "
            "should be available in 'only_parents' option",
        )
        self.assertNotIn(
            self.partner_child,
            self.sale_order_option_only_parents.available_partners,
            "Child and contact type partner"
            " shouldn't be available in 'only_parents' option",
        )
        self.assertNotIn(
            self.partner_diff_company,
            self.sale_order_option_only_parents.available_partners,
            "Partner from another company"
            " shouldn't be available on this company (option 'only_parents')",
        )
        self.assertNotIn(
            self.partner_delivery,
            self.sale_order_option_only_parents.available_partners,
            "Child and other type partner"
            " shouldn't be available in 'only_parents' option",
        )

    def test_sale_order_partner_restrict_option_parents_and_contacts(self):
        self.main_company.sale_order_partner_restrict = "parents_and_contacts"
        self.sale_order_option_parents_and_contacts = self._create_sale_order()

        self.assertIn(
            self.partner_parent,
            self.sale_order_option_parents_and_contacts.available_partners,
            "Parent and contact type partner"
            " should be available in 'parents_and_contacts' option",
        )
        self.assertIn(
            self.partner_child,
            self.sale_order_option_parents_and_contacts.available_partners,
            "Child and contact type partner"
            " should be available in 'parents_and_contacts' option",
        )
        self.assertNotIn(
            self.partner_diff_company,
            self.sale_order_option_parents_and_contacts.available_partners,
            "Partner from another company"
            " shouldn't be available on this company (option 'parents_and_contacts')",
        )
        self.assertNotIn(
            self.partner_delivery,
            self.sale_order_option_parents_and_contacts.available_partners,
            "Child and other type partner"
            " shouldn't be available in 'parents_and_contacts' option",
        )
