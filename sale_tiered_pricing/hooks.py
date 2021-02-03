# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    """This computation could be very long on an existing database."""
    query = (
        "ALTER TABLE sale_order_line ADD COLUMN IF NOT EXISTS is_tier_priced BOOLEAN;"
        "UPDATE sale_order_line SET is_tier_priced=false;"
    )
    cr.execute(query)
