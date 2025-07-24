# -*- coding: utf-8 -*-
{
    'name': 'Bookstore',
    'version': '1.0',
    'summary': 'Simple Bookstore module',
    'description': 'A simple Odoo 18 module for managing books in a bookstore.',
    'author': 'Your Name',
    'category': 'Sales',
    'depends': ['base'],
    'data': [
        'views/book_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
