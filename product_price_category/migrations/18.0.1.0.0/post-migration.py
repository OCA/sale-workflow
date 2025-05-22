# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        UPDATE product_pricelist_item
        SET display_applied_on = '2b_product_price_category'
        WHERE applied_on = '2b_product_price_category'
    """)
