# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


def migrate(cr, version):
    # If the addon was already installed on the current DB
    # we want to make the commitment date mandatory like in
    # previous version
    if version:
        query = """
            UPDATE res_company
            SET sale_commitment_date_required = true;
        """
        cr.execute(query)
