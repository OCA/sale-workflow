# Copyright 2022 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
