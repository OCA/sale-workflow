# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
_logger = logging.getLogger(__name__)

from odoo import api, models, fields, _

class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    is_cashondelivery = fields.Boolean(
        string='Is cashondelivery?',
        default=False
    )
    minimum_amount_cashondelivery = fields.Float(
        string='Minimum amount cashondelivery'
    )