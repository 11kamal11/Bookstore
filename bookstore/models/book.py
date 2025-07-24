# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class Book(models.Model):
    _name = 'bookstore.book'
    _description = 'Book'
    _order = 'name'
    _inherit = ['website.seo.metadata', 'website.published.mixin']

    name = fields.Char(string='Title', required=True)
    author = fields.Char(string='Author', required=True)
    isbn = fields.Char(string='ISBN', size=13)
    price = fields.Float(string='Price', required=True)
    cost_price = fields.Float(string='Cost Price')
    description = fields.Html(string='Description')  # Changed to Html for rich text
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
    
    # E-commerce fields
    website_published = fields.Boolean(string='Published on Website', default=True)
    image = fields.Image(string='Book Cover', max_width=1024, max_height=1024)
    image_medium = fields.Image(string='Medium Image', related='image', store=True, max_width=256, max_height=256)
    image_small = fields.Image(string='Small Image', related='image', store=True, max_width=128, max_height=128)
    sale_ok = fields.Boolean(string='Can be Sold', default=True)
    purchase_ok = fields.Boolean(string='Can be Purchased', default=True)
    
    # Sales and inventory
    list_price = fields.Float(string='Sales Price', related='price', store=True)
    standard_price = fields.Float(string='Cost', related='cost_price', store=True)
    qty_available = fields.Float(string='Quantity On Hand', related='stock_quantity', store=True)
    
    # Ratings and reviews
    rating = fields.Float(string='Average Rating', compute='_compute_rating', store=True)
    review_count = fields.Integer(string='Review Count', compute='_compute_rating', store=True)
    
    # Sales statistics
    sales_count = fields.Integer(string='Number of Sales', default=0)
    
    # Computed fields
    profit_margin = fields.Float(string='Profit Margin (%)', compute='_compute_profit_margin', store=True)
    age_years = fields.Integer(string='Age (Years)', compute='_compute_age_years')
    is_available = fields.Boolean(string='Available', compute='_compute_is_available')
    website_url = fields.Char(string='Website URL', compute='_compute_website_url')
    
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
    
    def _compute_website_url(self):
        for book in self:
            book.website_url = '/bookstore/book/%s' % book.id
    
    @api.depends('review_ids.rating')
    def _compute_rating(self):
        for record in self:
            reviews = record.review_ids.filtered(lambda r: r.rating > 0)
            if reviews:
                record.rating = sum(reviews.mapped('rating')) / len(reviews)
                record.review_count = len(reviews)
            else:
                record.rating = 0.0
                record.review_count = 0
    
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
    
    def action_add_to_cart(self):
        """Action to add book to cart"""
        return {
            'type': 'ir.actions.act_url',
            'url': '/shop/cart/update',
            'target': 'new',
        }


class BookCategory(models.Model):
    _name = 'bookstore.category'
    _description = 'Book Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
    book_ids = fields.One2many('bookstore.book', 'category_id', string='Books')
    book_count = fields.Integer(string='Number of Books', compute='_compute_book_count')
    image = fields.Image(string='Category Image', max_width=512, max_height=512)
    
    @api.depends('book_ids')
    def _compute_book_count(self):
        for record in self:
            record.book_count = len(record.book_ids.filtered('active'))


class BookReview(models.Model):
    _name = 'bookstore.book.review'
    _description = 'Book Review'
    _order = 'create_date desc'

    book_id = fields.Many2one('bookstore.book', string='Book', required=True, ondelete='cascade')
    customer_name = fields.Char(string='Customer Name', required=True)
    customer_email = fields.Char(string='Customer Email')
    rating = fields.Selection([
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ], string='Rating', required=True)
    review_text = fields.Text(string='Review')
    create_date = fields.Datetime(string='Review Date', default=fields.Datetime.now)
    is_published = fields.Boolean(string='Published', default=True)


# Add review relation to Book model
Book.review_ids = fields.One2many('bookstore.book.review', 'book_id', string='Reviews')
