from odoo import _, fields, models
from odoo.exceptions import UserError


class WizardPriceConfigMatrix(models.TransientModel):
    _name = "wizard.price.config.matrix"
    _description = "wizard to add a excel matrix to a price line"

    price_config_line_id = fields.Many2one(comodel_name="sale.price.config.line")
    horizontal_value = fields.Many2one(comodel_name="ir.model.fields", string="Horiz")
    vertical_value = fields.Many2one(comodel_name="ir.model.fields", string="Vert")
    target_field_domain = fields.Binary(
        related="price_config_line_id.target_field_domain"
    )
    matrix = fields.Text(string="Price matrix")

    def write(self, vals):
        res = super().write(vals)
        if "matrix" in vals and ";" not in vals["matrix"]:
            lines_string = vals["matrix"].split("\n")
            matrix = []
            for line in lines_string:
                new_line = line.split("\t")
                new_line = [e for e in new_line if e != ""]
                matrix.append(new_line)
            csv_string = ""

            first_line_length = len(matrix[0])

            for line in matrix[1:]:
                if len(line) != first_line_length:
                    raise UserError(_("Matrix is not properly formatted"))

            for i_l, line in enumerate(matrix):
                for i, el in enumerate(line):
                    csv_string += el
                    if i < len(line) - 1:
                        csv_string += ";"
                if i_l < len(matrix) - 1:
                    csv_string += "\n"
            self.price_config_line_id.matrix_values = csv_string

        if "vertical_value" in vals:
            self.price_config_line_id.vertical_value = vals["vertical_value"]
        if "horizontal_value" in vals:
            self.price_config_line_id.horizontal_value = vals["horizontal_value"]
        return res
