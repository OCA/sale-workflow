# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    cr.execute("""
    ALTER TABLE sale_order_line ADD COLUMN last_delivery_date TIMESTAMP;""")
