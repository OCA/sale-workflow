from odoo import api, fields, models

from odoo.addons.mrp_bom_configurable.models.mrp_bom_line import check_domain


class SalePriceConfig(models.Model):
    _name = "sale.price.config"
    _description = (
        "Configuration to compute the price of a product depending on an input config"
    )

    product_id = fields.Many2one(comodel_name="product.template", string="Product")

    sale_price_config_line_ids = fields.One2many(
        comodel_name="sale.price.config.line", inverse_name="sale_price_config_id"
    )

    def _get_price(self, input_line):
        price = 0

        for rec in self:
            for i, line in enumerate(rec.sale_price_config_line_ids):
                if check_domain(
                    line.domain,
                    input_line._get_input_line_values(),
                    f"line {i}",
                    f"config {self.product_id.name}",
                ):
                    price += line._get_price(input_line)

        return price


class SalePriceConfigLine(models.Model):
    _name = "sale.price.config.line"
    _description = "Component of sale price config"
    _order = "sequence,id"

    sequence = fields.Integer(
        default=10, help="Gives the sequence order when displaying a list of records."
    )
    sale_price_config_id = fields.Many2one(comodel_name="sale.price.config")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    line_type = fields.Selection(
        selection=[
            ("base", "Fixed amount"),
            ("factor", "Multiply amount by field value"),
            ("include_product_or_category", "Include product or category"),
            ("matrix", "Matrice"),
        ],
        string="Type",
        required=True,
    )
    horizontal_value = fields.Many2one(comodel_name="ir.model.fields", string="Horiz")
    vertical_value = fields.Many2one(comodel_name="ir.model.fields", string="Vert")
    matrix_values = fields.Text()

    target_field = fields.Many2one(comodel_name="ir.model.fields", string="Field")
    target_field_domain = fields.Binary(
        compute="_compute_target_field_domain", readonly=True, store=False
    )

    included_product_or_category = fields.Reference(
        selection=[("product.template", "Product"), ("product.category", "Category")],
        string="Included product or category",
    )

    domain = fields.Char()

    amount = fields.Float(digits=(12, 4))

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
                    if (
                        res_id._name == "product.category"
                        and line["product_tmpl_id"].categ_id.id == res_id.id
                    ):
                        return line["product_tmpl_id"].list_price * line["product_qty"]
                    if (
                        res_id._name == "product.template"
                        and line["product_tmpl_id"].id == res_id.id
                    ):
                        return line["product_tmpl_id"].list_price * line["product_qty"]
                return 0.0
            case "factor":
                factor = input_line[self.target_field.name]
                return factor * self.amount
            case "matrix":
                horiz_target = input_line[self.horizontal_value.name]
                vert_target = input_line[self.vertical_value.name]
                lines = self.matrix_values.split("\n")
                matrix_data = []
                for line in lines:
                    matrix_data.append(line.split(";"))

                horiz_values = matrix_data[0][1:]
                vert_values = []

                for line in matrix_data[1:]:
                    vert_values.append(line[0])

                horiz_index = 1
                while float(horiz_values[horiz_index - 1]) < horiz_target:
                    horiz_index += 1

                vert_index = 1
                while float(horiz_values[vert_index - 1]) < vert_target:
                    vert_index += 1
                return float(matrix_data[vert_index][horiz_index])

    def open_matrix_wizard(self):
        wizard_id = self.env["wizard.price.config.matrix"].create(
            {
                "price_config_line_id": self.id,
                "horizontal_value": self.horizontal_value.id,
                "vertical_value": self.vertical_value.id,
                "matrix": self.matrix_values,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Add price matrix",
            "res_model": "wizard.price.config.matrix",
            "view_mode": "form",
            "target": "new",
            "res_id": wizard_id.id,
        }
