# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Book(models.Model):
    _name = 'bookstore.book'
    _description = 'Book'
    _rec_name = 'name'

    name = fields.Char('Book Title', required=True)
    author = fields.Char('Author', required=True)
    isbn = fields.Char('ISBN')
    price = fields.Float('Price')
    description = fields.Text('Description')
    category_id = fields.Many2one('bookstore.category', string='Category')
    is_published = fields.Boolean('Published on Website', default=True)
    
    def action_publish_website(self):
        """Publish book on website"""
        self.write({'is_published': True})
    
    def action_unpublish_website(self):
        """Unpublish book from website"""
        self.write({'is_published': False})


class BookCategory(models.Model):
    _name = 'bookstore.category'
    _description = 'Book Category'
    _rec_name = 'name'

    name = fields.Char('Category Name', required=True)
    description = fields.Text('Description')
    book_ids = fields.One2many('bookstore.book', 'category_id', string='Books')
