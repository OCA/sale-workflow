# Copyright 2014 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2020 Camptocamp SA (author: Simone Orsi)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))


class TestAutomaticWorkflowMixin:
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


@tagged("post_install", "-at_install")
class TestMultiCompanyCommon(AccountTestInvoicingCommon):
    @classmethod
    def create_product(cls, values):
        values.update({"type": "consu", "invoice_policy": "order"})
        product_template = cls.env["product.template"].create(values)
        return product_template.product_variant_id

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                # Compatibility with sale_automatic_workflow_job: even if
                # the module is installed, ensure we don't delay a job.
                # Thus, we test the usual flow.
                _job_force_sync=True,
            )
        )
        cls.company_fr = cls.setup_company_data(
            {
                "name": "French company",
                "currency_id": cls.env.ref("base.EUR").id,
                "country_id": cls.env.ref("base.fr").id,
            }
        )["company"]

        cls.company_ch = cls.setup_company_data(
            {
                "name": "Swiss company",
                "currency_id": cls.env.ref("base.CHF").id,
                "country_id": cls.env.ref("base.ch").id,
            }
        )["company"]

        cls.company_be = cls.setup_company_data(
            {
                "name": "Belgian company",
                "currency_id": cls.env.ref("base.EUR").id,
                "country_id": cls.env.ref("base.be").id,
            }
        )["company"]

        cls.company_fr_daughter = cls.setup_company_data(
            {
                "name": "French company daughter",
                "currency_id": cls.env.ref("base.EUR").id,
                "country_id": cls.env.ref("base.fr").id,
            }
        )["company"]

        cls.env.user.company_ids |= cls.company_fr
        cls.env.user.company_ids |= cls.company_ch
        cls.env.user.company_ids |= cls.company_be
        cls.env.user.company_ids |= cls.company_fr_daughter

        cls.env.user.company_id = cls.company_fr.id
        cls.customer_fr = (
            cls.env["res.partner"]
            .with_context(default_company_id=cls.company_fr.id)
            .create({"name": "Customer FR"})
        )
        cls.product_fr = cls.create_product({"name": "Evian bottle", "list_price": 2.0})

        cls.env.user.company_id = cls.company_ch.id

        cls.customer_ch = cls.env["res.partner"].create({"name": "Customer CH"})
        cls.product_ch = cls.create_product(
            {"name": "Henniez bottle", "list_price": 3.0}
        )

        cls.env.user.company_id = cls.company_be.id
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
        cls.customer_fr_daughter = cls.env["res.partner"].create(
            {"name": "Customer FR Daughter"}
        )
        cls.product_fr_daughter = cls.create_product(
            {"name": "Contrex bottle", "list_price": 1.5}
        )

        cls.auto_wkf = cls.env.ref("sale_automatic_workflow.automatic_validation")
        cls.env.user.company_id = cls.env.ref("base.main_company")

    def create_auto_wkf_order(self, company, customer, product, qty):
        # We need to change to the proper company
        # to pick up correct company dependent fields
        SaleOrder = self.env["sale.order"].with_company(company)

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
        return order
