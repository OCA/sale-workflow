from odoo import api, fields, models


class WizSalePriceConfigChange(models.TransientModel):
    _name = "wizard.sale.price.config.change"
    _description = "Change of sale price"

    percentage = fields.Float()
    price_config_line_ids = fields.Many2many(comodel_name="sale.price.config.line")
    start_of_change = fields.Datetime(string="Start of price change")

    def change_amount(self, price_amount):
        return round(price_amount * (1 + self.percentage))

    def _prepare_line_data_from_old(self, new_config_id, line_id):
        new_line_data = line_id.copy_data()[0]
        new_line_data["sale_price_config_id"] = new_config_id.id
        match line_id.line_type:
            case "base" | "factor":
                new_line_data["amount"] = self.change_amount(new_line_data["amount"])
            case "matrix":
                new_matrix = ""
                matrix = new_line_data["matrix_values"]
                matrix_lines = matrix.split("\n")
                for i_l, matrix_line in enumerate(matrix_lines):
                    new_matrix_line = ""
                    new_matrix_line_data = []
                    if i_l == 0:
                        new_matrix_line = matrix_line
                    else:
                        line_data = matrix_line.split(";")
                        new_matrix_line_data.append(line_data[0])
                        for element in line_data[1:]:
                            if element == "-1":
                                new_matrix_line_data.append(element)
                            else:
                                new_matrix_line_data.append(
                                    str(self.change_amount(int(element)))
                                )
                        new_matrix_line = ";".join(new_matrix_line_data)
                    new_matrix += new_matrix_line + "\n"
                new_line_data["matrix_values"] = new_matrix
        return new_line_data

    def copy_and_modify_line(self, config_id, lines_to_modify):
        config_id.end_date = self.start_of_change
        new_config_id = self.env["sale.price.config"].create(
            {"start_date": self.start_of_change, "product_id": config_id.product_id.id}
        )

        for line in config_id.sale_price_config_line_ids:
            new_line_data = None
            if line.id in lines_to_modify:
                new_line_data = self._prepare_line_data_from_old(new_config_id, line)
            else:
                new_line_data = line.copy_data()[0]
            self.env["sale.price.config.line"].create(new_line_data)

    def apply_change(self):
        self.ensure_one()
        line_by_config_id = {}
        for line in self.price_config_line_ids:
            if line.sale_price_config_id.id not in line_by_config_id:
                line_by_config_id[line.sale_price_config_id.id] = {
                    "price_config": line.sale_price_config_id,
                    "lines": [],
                }
            line_by_config_id[line.sale_price_config_id.id]["lines"].append(line.id)

        for _, data in line_by_config_id.items():
            if len(data["lines"]) > 0:
                self.copy_and_modify_line(data["price_config"], data["lines"])

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            rec.apply_change()
        return res
