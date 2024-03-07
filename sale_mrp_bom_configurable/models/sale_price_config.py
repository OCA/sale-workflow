from odoo import api, fields, models
from odoo.exceptions import UserError


class SalePriceConfig(models.Model):
    _name = "sale.price.config"

    product_id = fields.Many2one(comodel_name="product.template", string="Product")

    sale_price_config_line_ids = fields.One2many(
        comodel_name="sale.price.config.line", inverse_name="sale_price_config_id"
    )

    def _get_price(self, input_line):
        price = 0

        for rec in self:
            for line in rec.sale_price_config_line_ids:
                price += line._get_price(input_line)

        return price


class SalePriceConfigLine(models.Model):
    _name = "sale.price.config.line"

    sale_price_config_id = fields.Many2one(comodel_name="sale.price.config")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    line_type = fields.Selection(
        selection=[
            ("base", "Base"),
            ("factor", "Multiply"),
            ("include_product_or_category", "Include product or category"),
        ],
        string="Type",
        required=True,
    )

    target_field = fields.Many2one(comodel_name="ir.model.fields", string="Field")
    target_field_domain = fields.Binary(
        compute="_compute_target_field_domain", readonly=True, store=False
    )

    included_product_or_category = fields.Reference(
        selection=[("product.template", "Product"), ("product.category", "Category")],
        string="Included product or category",
    )

    domain = fields.Char()

    amount = fields.Monetary(currency_field="currency_id")

    currency_id = fields.Many2one(
        related="company_id.currency_id", string="Company Currency", store=True
    )

    @api.depends("line_type")
    def _compute_target_field_domain(self):
        for rec in self:
            input_line_model = self.env["ir.model"].search(
                [("model", "=", "input.line")]
            )
            rec.target_field_domain = [
                (
                    "model_id",
                    "=",
                    input_line_model.id,
                )
            ]

    def _get_price(self, input_line):
        self.ensure_one()
        match self.line_type:
            case "base":
                return self.amount
            case "include_product_or_category":
                lines = input_line.create_bom_line_data()
                res_id = self.included_product_or_category
                for line in lines:
                    if res_id._name == "product.category" and line["product_tmpl_id"].categ_id.id == res_id.id:
                        return (
                            line["product_tmpl_id"].list_price * line["product_qty"]
                        )
                    if res_id._name == "product.template" and line["product_tmpl_id"].id == res_id.id:
                        return (
                            line["product_tmpl_id"].list_price * line["product_qty"]
                        )
                return 0.0
            case "factor":
                factor = input_line[self.target_field.name]
                return factor * self.amount
