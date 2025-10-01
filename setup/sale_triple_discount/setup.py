import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'depends_override': {
            'account_invoice_triple_discount': 'odoo-addon-account-invoice-triple-discount<16.0.3.0.0',
        },
    }
)
