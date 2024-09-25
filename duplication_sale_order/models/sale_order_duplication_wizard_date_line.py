# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class SaleOrderDuplicationWizardDateLine(models.TransientModel):
    _name = "sale.order.duplication.wizard.date.line"
    _description = "Sale Order Duplication Wizard Line"

    wizard_id = fields.Many2one(comodel_name="sale.order.duplication.wizard")

    commitment_date = fields.Date(string="Delivery Date", required=True)
