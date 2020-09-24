# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2020 Camptocamp SA (author: Simone Orsi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))


class TestAutomaticWorkflowMixin(object):
    def create_sale_order(self, workflow, override=None, product_type="consu"):
        sale_obj = self.env["sale.order"]

        partner_values = {"name": "Imperator Caius Julius Caesar Divus"}
        partner = self.env["res.partner"].create(partner_values)

        product_values = {"name": "Bread", "list_price": 5, "type": product_type}
        product = self.env["product.product"].create(product_values)
        self.product_uom_unit = self.env.ref("uom.product_uom_unit")
        values = {
            "partner_id": partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom": self.product_uom_unit.id,
                        "price_unit": product.list_price,
                        "product_uom_qty": 1,
                    },
                )
            ],
            "workflow_process_id": workflow.id,
        }
        if override:
            values.update(override)
        return sale_obj.create(values)

    def create_full_automatic(self, override=None):
        workflow_obj = self.env["sale.workflow.process"]
        values = workflow_obj.create(
            {
                "name": "Full Automatic",
                "validate_order": True,
                "create_invoice": True,
                "validate_invoice": True,
                "invoice_date_is_order_date": True,
            }
        )
        if override:
            values.update(override)
        return values

    def run_job(self):
        self.env["automatic.workflow.job"].run()


class TestMultiCompanyCommon(TestCommon):
    """Common class for multi-company related tests."""

    @classmethod
    def create_company(cls, values):
        return cls.env["res.company"].create(values)

    @classmethod
    def create_product(cls, values):
        values.update({"type": "consu", "invoice_policy": "order"})
        product_template = cls.env["product.template"].create(values)
        return product_template.product_variant_id

    @classmethod
    def setUpClass(cls):
        """Setup data for all test cases."""
        super().setUpClass()
        coa = cls.env.user.company_id.chart_template_id
        cls.company_fr = cls.create_company(
            {
                "name": "French company",
                "currency_id": cls.env.ref("base.EUR").id,
                "country_id": cls.env.ref("base.fr").id,
            }
        )

        cls.company_ch = cls.create_company(
            {
                "name": "Swiss company",
                "currency_id": cls.env.ref("base.CHF").id,
                "country_id": cls.env.ref("base.ch").id,
            }
        )

        cls.company_be = cls.create_company(
            {
                "name": "Belgian company",
                "currency_id": cls.env.ref("base.EUR").id,
                "country_id": cls.env.ref("base.be").id,
            }
        )

        cls.company_fr_daughter = cls.create_company(
            {
                "name": "French company daughter",
                "currency_id": cls.env.ref("base.EUR").id,
                "country_id": cls.env.ref("base.fr").id,
            }
        )

        cls.env.user.company_ids |= cls.company_fr
        cls.env.user.company_ids |= cls.company_ch
        cls.env.user.company_ids |= cls.company_be
        cls.env.user.company_ids |= cls.company_fr_daughter

        cls.env.user.company_id = cls.company_fr.id
        coa.try_loading_for_current_company()
        cls.customer_fr = cls.env["res.partner"].create({"name": "Customer FR"})
        cls.product_fr = cls.create_product({"name": "Evian bottle", "list_price": 2.0})

        cls.env.user.company_id = cls.company_ch.id
        coa.try_loading_for_current_company()
        cls.customer_ch = cls.env["res.partner"].create({"name": "Customer CH"})
        cls.product_ch = cls.create_product(
            {"name": "Henniez bottle", "list_price": 3.0}
        )

        cls.env.user.company_id = cls.company_be.id
        coa.try_loading_for_current_company()
        cls.customer_be = cls.env["res.partner"].create({"name": "Customer BE"})
        cls.product_be = (
            cls.env["product.template"]
            .create(
                {
                    "name": "SPA bottle",
                    "list_price": 1.5,
                    "type": "consu",
                    "invoice_policy": "order",
                }
            )
            .product_variant_id
        )

        cls.env.user.company_id = cls.company_fr_daughter.id
        coa.try_loading_for_current_company()
        cls.customer_fr_daughter = cls.env["res.partner"].create(
            {"name": "Customer FR Daughter"}
        )
        cls.product_fr_daughter = cls.create_product(
            {"name": "Contrex bottle", "list_price": 1.5}
        )

        cls.auto_wkf = cls.env.ref("sale_automatic_workflow.automatic_validation")
        cls.env.user.company_id = cls.env.ref("base.main_company")

    def create_auto_wkf_order(self, company, customer, product, qty):
        SaleOrder = self.env["sale.order"]

        self.product_uom_unit = self.env.ref("uom.product_uom_unit")

        order = SaleOrder.create(
            {
                "partner_id": customer.id,
                "company_id": company.id,
                "workflow_process_id": self.auto_wkf.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "price_unit": product.list_price,
                            "product_uom_qty": qty,
                            "product_uom": self.product_uom_unit.id,
                        },
                    )
                ],
            }
        )
        order._onchange_workflow_process_id()
        return order
