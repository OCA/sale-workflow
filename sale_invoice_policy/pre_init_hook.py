# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    """
    As we change the invoice policy to computed field, we must initialize
    the default policy with original values
    """
    cr.execute(
        "ALTER TABLE product_template ADD COLUMN IF NOT EXISTS default_invoice_policy VARCHAR"
    )
    query = """
     UPDATE product_template
     SET default_invoice_policy = invoice_policy
     WHERE invoice_policy IS NOT NULL"""
    cr.execute(query)
