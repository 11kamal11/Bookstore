# -*- coding: utf-8 -*-
{
    'name': 'Bookstore',
    'version': '1.0',
    'summary': 'Simple Bookstore module with Website',
    'description': 'A simple Odoo 18 module for managing books in a bookstore with frontend website.',
    'author': 'Kamal',
    'category': 'Sales',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/book_view.xml',
        'views/website_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
