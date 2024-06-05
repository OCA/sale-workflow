from odoo import fields, models


class WizardCopyInputLineData(models.TransientModel):
    _name = "wizard.copy.input.line.data"
    _description = "Wizard model to copy input_line data to all line in a input_config"

    input_config_id = fields.Many2one(comodel_name="input.config")
    input_line_id = fields.Many2one(comodel_name="input.line")
    line_ids = fields.One2many(
        comodel_name="wizard.copy.input.line.data.line", inverse_name="wizard_id"
    )

    def create(self, vals):
        lines = []
        input_line_id = self.env["input.line"].browse(vals["input_line_id"])
        for el in input_line_id._get_config_elements():
            line = self.env["wizard.copy.input.line.data.line"].create(
                {
                    "wizard_id": self.id,
                    "field_name": el,
                    "should_copy": False,
                }
            )
            lines.append(line.id)
        vals["line_ids"] = [(6, 0, lines)]
        return super().create(vals)

    def write(self, vals):
        res = super().write(vals)
        for input_line in self.input_config_id.line_ids:
            if input_line.id != self.input_line_id.id:
                for line in self.line_ids.search([("should_copy", "=", True)]):
                    input_line[line.field_name] = self.input_line_id[line.field_name]

        self.unlink()

        return res


class WizardCopyInputLineDataLine(models.TransientModel):
    _name = "wizard.copy.input.line.data.line"

    wizard_id = fields.Many2one(comodel_name="wizard.copy.input.line.data")
    field_name = fields.Char(String="Field name")
    should_copy = fields.Boolean(String="Copy")
