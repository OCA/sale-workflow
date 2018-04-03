{
    'name': 'Payment Signal',
    'description': 'Módulo para señalizar presupuestos y pedidos',
    'version': '1.1',
    'author': 'Amaro Pesquero',
    'application': True,
    'data': [
             'views/inherit_res_company.xml',
             'views/inherit_sale_order.xml', ],
    'category': 'Sales',
    'depends': ['account', 'sale'],
    'application': True,
}
