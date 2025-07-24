# -*- coding: utf-8 -*-
from odoo import models, fields

class Book(models.Model):
    _name = 'bookstore.book'
    _description = 'Book'

    name = fields.Char(string='Title', required=True)
    author = fields.Char(string='Author')
    price = fields.Float(string='Price')
    description = fields.Text(string='Description')
