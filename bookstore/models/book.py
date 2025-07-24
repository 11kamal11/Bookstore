# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class Book(models.Model):
    _name = 'bookstore.book'
    _description = 'Book'
    _order = 'name'

    name = fields.Char(string='Title', required=True)
    author = fields.Char(string='Author', required=True)
    isbn = fields.Char(string='ISBN', size=13)
    price = fields.Float(string='Price', required=True)
    cost_price = fields.Float(string='Cost Price')
    description = fields.Text(string='Description')
    category_id = fields.Many2one('bookstore.category', string='Category')
    publication_date = fields.Date(string='Publication Date')
    pages = fields.Integer(string='Number of Pages')
    language = fields.Selection([
        ('en', 'English'),
        ('fr', 'French'),
        ('es', 'Spanish'),
        ('de', 'German'),
        ('it', 'Italian'),
    ], string='Language', default='en')
    stock_quantity = fields.Integer(string='Stock Quantity', default=0)
    active = fields.Boolean(string='Active', default=True)
    publisher = fields.Char(string='Publisher')
    edition = fields.Char(string='Edition')
    
    # Computed fields
    profit_margin = fields.Float(string='Profit Margin (%)', compute='_compute_profit_margin', store=True)
    age_years = fields.Integer(string='Age (Years)', compute='_compute_age_years')
    is_available = fields.Boolean(string='Available', compute='_compute_is_available')
    
    @api.depends('price', 'cost_price')
    def _compute_profit_margin(self):
        for record in self:
            if record.cost_price and record.price:
                record.profit_margin = ((record.price - record.cost_price) / record.cost_price) * 100
            else:
                record.profit_margin = 0.0
    
    @api.depends('publication_date')
    def _compute_age_years(self):
        for record in self:
            if record.publication_date:
                today = date.today()
                record.age_years = today.year - record.publication_date.year
            else:
                record.age_years = 0
    
    @api.depends('stock_quantity')
    def _compute_is_available(self):
        for record in self:
            record.is_available = record.stock_quantity > 0
    
    @api.constrains('isbn')
    def _check_isbn(self):
        for record in self:
            if record.isbn and len(record.isbn) not in [10, 13]:
                raise ValidationError("ISBN must be 10 or 13 characters long.")
    
    @api.constrains('price', 'cost_price')
    def _check_prices(self):
        for record in self:
            if record.price < 0:
                raise ValidationError("Price cannot be negative.")
            if record.cost_price < 0:
                raise ValidationError("Cost price cannot be negative.")


class BookCategory(models.Model):
    _name = 'bookstore.category'
    _description = 'Book Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
    book_ids = fields.One2many('bookstore.book', 'category_id', string='Books')
    book_count = fields.Integer(string='Number of Books', compute='_compute_book_count')
    
    @api.depends('book_ids')
    def _compute_book_count(self):
        for record in self:
            record.book_count = len(record.book_ids)
