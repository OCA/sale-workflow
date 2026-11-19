# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'res_partner' AND column_name = 'sale_incoterm_id'
        """
    )
    if not cr.fetchone():
        return
    cr.execute(
        """
        UPDATE res_partner
        SET incoterm_id = sale_incoterm_id
        WHERE sale_incoterm_id IS NOT NULL AND incoterm_id IS NULL
        """
    )
