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
        ('ar', 'Arabic'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
    ], string='Language', default='en')
    stock_quantity = fields.Integer(string='Stock Quantity', default=0)
    active = fields.Boolean(string='Active', default=True)
    publisher = fields.Char(string='Publisher')
    edition = fields.Char(string='Edition')
    
    # New enhanced fields
    book_format = fields.Selection([
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
        ('ebook', 'E-book'),
        ('audiobook', 'Audiobook'),
    ], string='Format', default='paperback')
    
    condition = fields.Selection([
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('acceptable', 'Acceptable'),
    ], string='Condition', default='new')
    
    weight = fields.Float(string='Weight (kg)')
    dimensions = fields.Char(string='Dimensions (L x W x H)')
    genre = fields.Char(string='Genre')
    tags = fields.Char(string='Tags (comma separated)')
    featured = fields.Boolean(string='Featured Book', default=False)
    
    # Stock management
    min_stock_level = fields.Integer(string='Minimum Stock Level', default=5)
    reorder_quantity = fields.Integer(string='Reorder Quantity', default=20)
    supplier_id = fields.Many2one('res.partner', string='Supplier', domain=[('is_company', '=', True)])
    
    # Sales tracking
    total_sold = fields.Integer(string='Total Sold', default=0)
    last_sale_date = fields.Date(string='Last Sale Date')
    
    # Computed fields
    profit_margin = fields.Float(string='Profit Margin (%)', compute='_compute_profit_margin', store=True)
    age_years = fields.Integer(string='Age (Years)', compute='_compute_age_years')
    is_available = fields.Boolean(string='Available', compute='_compute_is_available')
    stock_status = fields.Selection([
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ], string='Stock Status', compute='_compute_stock_status')
    total_value = fields.Float(string='Total Inventory Value', compute='_compute_total_value')
    
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
    
    @api.depends('stock_quantity', 'min_stock_level')
    def _compute_stock_status(self):
        for record in self:
            if record.stock_quantity <= 0:
                record.stock_status = 'out_of_stock'
            elif record.stock_quantity <= record.min_stock_level:
                record.stock_status = 'low_stock'
            else:
                record.stock_status = 'in_stock'
    
    @api.depends('stock_quantity', 'cost_price')
    def _compute_total_value(self):
        for record in self:
            record.total_value = record.stock_quantity * (record.cost_price or 0)
    
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
    
    def action_restock(self):
        """Action to restock the book"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Restock Book',
            'res_model': 'bookstore.restock.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_book_id': self.id}
        }
    
    def action_mark_as_featured(self):
        """Mark book as featured"""
        self.featured = True
    
    def action_unmark_as_featured(self):
        """Unmark book as featured"""
        self.featured = False
    
    def action_view_stock_logs(self):
        """View stock movement logs for this book"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Stock Movements - {self.name}',
            'res_model': 'bookstore.stock.log',
            'view_mode': 'tree,form',
            'domain': [('book_id', '=', self.id)],
            'context': {'default_book_id': self.id}
        }


class BookCategory(models.Model):
    _name = 'bookstore.category'
    _description = 'Book Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    parent_id = fields.Many2one('bookstore.category', string='Parent Category')
    child_ids = fields.One2many('bookstore.category', 'parent_id', string='Child Categories')
    
    # Enhanced category fields
    category_code = fields.Char(string='Category Code', size=10)
    display_order = fields.Integer(string='Display Order', default=10)
    featured = fields.Boolean(string='Featured Category', default=False)
    category_manager_id = fields.Many2one('res.users', string='Category Manager')
    
    book_ids = fields.One2many('bookstore.book', 'category_id', string='Books')
    
    # Computed fields
    book_count = fields.Integer(string='Number of Books', compute='_compute_book_count')
    total_books_value = fields.Float(string='Total Books Value', compute='_compute_total_books_value')
    avg_book_price = fields.Float(string='Average Book Price', compute='_compute_avg_book_price')
    in_stock_books = fields.Integer(string='In Stock Books', compute='_compute_in_stock_books')
    
    @api.depends('book_ids')
    def _compute_book_count(self):
        for record in self:
            record.book_count = len(record.book_ids.filtered('active'))
    
    @api.depends('book_ids.price', 'book_ids.stock_quantity')
    def _compute_total_books_value(self):
        for category in self:
            total = sum(book.price * book.stock_quantity for book in category.book_ids)
            category.total_books_value = total
    
    @api.depends('book_ids.price')
    def _compute_avg_book_price(self):
        for category in self:
            if category.book_ids:
                category.avg_book_price = sum(category.book_ids.mapped('price')) / len(category.book_ids)
            else:
                category.avg_book_price = 0.0
    
    @api.depends('book_ids.stock_quantity')
    def _compute_in_stock_books(self):
        for category in self:
            category.in_stock_books = len(category.book_ids.filtered(lambda b: b.stock_quantity > 0))
    
    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        for category in self:
            if not category._check_recursion():
                raise ValidationError("You cannot create recursive categories.")
    
    def action_view_books(self):
        """Action to view books in this category"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Books in {self.name}',
            'res_model': 'bookstore.book',
            'view_mode': 'tree,form',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id}
        }
