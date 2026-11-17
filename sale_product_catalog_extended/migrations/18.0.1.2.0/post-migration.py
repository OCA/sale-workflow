# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """The Price section of the catalog search panel is now hidden unless it is
    enabled in the settings: keep it shown in the existing databases."""
    cr.execute(
        """
        INSERT INTO ir_config_parameter (key, value, create_uid, create_date,
            write_uid, write_date)
        VALUES ('sale_product_catalog_extended.catalog_show_price_mode', 'True',
            1, now() at time zone 'UTC', 1, now() at time zone 'UTC')
        ON CONFLICT (key) DO NOTHING
        """
    )
