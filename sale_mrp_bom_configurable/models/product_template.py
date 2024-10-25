from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _find_price_config(self):
        return self.env["sale.price.config"].search(
            [
                ("product_id", "=", self.id),
                (
                    "start_date",
                    "<",
                    fields.Date.context_today(self).strftime("%Y-%m-%d 00:00:00"),
                ),
                "|",
                (
                    "end_date",
                    ">",
                    fields.Date.context_today(self).strftime("%Y-%m-%d 00:00:00"),
                ),
                ("end_date", "=", False),
            ]
        )[0]
