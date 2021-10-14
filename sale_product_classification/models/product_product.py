# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class ProductProduct(models.Model):
    _inherit = "product.product"

    sale_classification = fields.Selection(
        selection=[
            ("a", "A"),
            ("b", "B"),
            ("c", "C"),
            ("d", "D"),
        ],
        string="Sales classification",
        help="How the product performs according to sales",
        default="d",
        company_dependent=True,
    )
    seasonality_classification = fields.Selection(
        selection=[
            ("very high", "Very high"),
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
        string="Seasonility",
        help="Whether this product is selled during very short periods of time "
             "or steadily across the whole year",
        default="low",
        company_dependent=True,
    )

    def _get_product_performance(self, start, end):
        """Get aggregated products performance"""
        sales_report = self.env["sale.report"].read_group(
            [
                ("product_id", "in", self.ids),
                ("confirmation_date", ">=", fields.Datetime.to_string(start)),
                ("confirmation_date", "<=", fields.Datetime.to_string(end)),
                ("qty_delivered", ">", 0),
            ],
            ["price_subtotal", "product_uom_qty", "qty_delivered"],
            ["product_id"]
        )
        for result in sales_report:
            result["price_subtotal_delivered"] = (
                (
                    result.get("price_subtotal") / result.get("product_uom_qty")
                ) * result.get("qty_delivered")
            )
        return sales_report

    def action_get_sales_classification(self):
        """Compute every product classifications according to each company
        rules and sales"""
        company = self.env["res.company"].browse(
            self.env.context.get("company_id")
        ) or self.env.user.company_id
        days_to_ignore = company.sale_classification_days_to_ignore
        days_to_evaluate = company.sale_classification_days_to_evaluate
        sale_classification_a = company.sale_classification_a
        sale_classification_b = company.sale_classification_b
        sale_classification_c = company.sale_classification_c
        today = fields.Date.today()
        start = today - relativedelta(days=days_to_evaluate)
        up_to_date = today - relativedelta(days=days_to_ignore)
        products = self.search([
            ("id", "in", self.ids),
            ("create_date", "<=", fields.Datetime.to_string(up_to_date))
        ])
        sales_report = products._get_product_performance(start, today)
        products_a = self.browse([
            x.get("product_id")[0] for x in sales_report
            if x.get("price_subtotal_delivered") >= sale_classification_a
        ])
        products_b = self.browse([
            x.get("product_id")[0] for x in sales_report
            if x.get("price_subtotal_delivered") >= sale_classification_b
            and x.get("price_subtotal_delivered") < sale_classification_a
        ])
        products_c = self.browse([
            x.get("product_id")[0] for x in sales_report
            if x.get("price_subtotal_delivered") >= sale_classification_c
            and x.get("price_subtotal_delivered") < sale_classification_b
        ])
        products_d = products - products_a - products_b - products_c
        products_a.write({
            "sale_classification": "a",
        })
        products_b.write({
            "sale_classification": "b",
        })
        products_c.write({
            "sale_classification": "c",
        })
        products_d.write({
            "sale_classification": "d",
        })

    @api.model
    def cron_sales_classification(self):
        """Evaluate according company rules"""
        companies = self.env["res.company"].search([])
        products = self.search([])
        for company in companies:
            products.with_context(
                force_company=company.id
            ).action_get_sales_classification()
