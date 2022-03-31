# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


def migrate(cr, version):
    # Remove NOT NULL constraint of previous version
    query = """
        ALTER TABLE sale_order
        ALTER COLUMN commitment_date DROP NOT NULL;
    """
    cr.execute(query)
