from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    pdp_id = fields.Many2one("planned.down.payment")

    def unlink(self):
        for r in self:
            if r.pdp_id and r.pdp_id.state == "invoiced":
                r.pdp_id.state = "confirmed"
        super(AccountMove, self).unlink()
