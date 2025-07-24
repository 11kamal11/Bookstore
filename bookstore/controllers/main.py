# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class BookstoreController(http.Controller):

    @http.route('/bookstore/test', type='http', auth='public', website=True)
    def bookstore_test(self, **kwargs):
        """Simple test page to verify routing works"""
        return request.render('bookstore.bookstore_test', {})

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, search='', category=None, sort='name', **kwargs):
        """Display all books on the bookstore homepage with filtering and sorting"""
        domain = [('active', '=', True), ('website_published', '=', True)]
        
        # Search functionality
        if search:
            domain.extend([
                '|', '|',
                ('name', 'ilike', search),
                ('author', 'ilike', search),
                ('description', 'ilike', search)
            ])
        
        # Category filter
        if category:
            domain.append(('category_id', '=', int(category)))
        
        # Sorting options
        sort_options = {
            'name': 'name',
            'price_low': 'price',
            'price_high': 'price desc',
            'newest': 'publication_date desc',
            'rating': 'rating desc',
        }
        order = sort_options.get(sort, 'name')
        
        books = request.env['bookstore.book'].sudo().search(domain, order=order)
        categories = request.env['bookstore.category'].sudo().search([])
        current_category = None
        if category:
            current_category = request.env['bookstore.category'].sudo().browse(int(category))
        
        return request.render('bookstore.bookstore_home', {
            'books': books,
            'categories': categories,
            'current_category': current_category,
            'search_term': search,
            'current_sort': sort,
        })

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
        """Display detailed view of a single book"""
        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists() or not book.active or not book.website_published:
            return request.not_found()
        
        # Get related books from the same category
        related_books = request.env['bookstore.book'].sudo().search([
            ('category_id', '=', book.category_id.id),
            ('id', '!=', book.id),
            ('active', '=', True),
            ('website_published', '=', True)
        ], limit=4)
        
        # Get reviews
        reviews = book.review_ids.filtered('is_published')
        
        return request.render('bookstore.book_detail', {
            'book': book,
            'related_books': related_books,
            'reviews': reviews,
        })

    @http.route('/bookstore/add_to_cart', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def add_to_cart(self, book_id, quantity=1, **kwargs):
        """Add book to cart"""
        book = request.env['bookstore.book'].sudo().browse(int(book_id))
        if not book.exists():
            return request.not_found()
        
        # Check stock
        if book.stock_quantity < int(quantity):
            return request.render('bookstore.cart_error', {
                'error': f'Sorry, only {book.stock_quantity} items available in stock.',
                'book': book,
            })
        
        # Add to cart logic here
        order = request.website.sale_get_order(force_create=True)
        order._cart_update(
            product_id=book.id,
            add_qty=int(quantity),
        )
        
        return request.redirect('/shop/cart')

    @http.route('/bookstore/review/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def submit_review(self, book_id, customer_name, customer_email, rating, review_text='', **kwargs):
        """Submit a book review"""
        book = request.env['bookstore.book'].sudo().browse(int(book_id))
        if not book.exists():
            return request.not_found()
        
        # Create review
        request.env['bookstore.book.review'].sudo().create({
            'book_id': book.id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'rating': int(rating),
            'review_text': review_text,
        })
        
        return request.redirect(f'/bookstore/book/{book_id}?review_submitted=1')

    @http.route('/bookstore/category/<int:category_id>', type='http', auth='public', website=True)
    def books_by_category(self, category_id, **kwargs):
        """Display books filtered by category"""
        return self.bookstore_home(category=category_id, **kwargs)


class BookstoreWebsiteSale(WebsiteSale):
    """Extend website sale for bookstore specific functionality"""
    
    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """Override cart update to handle book stock"""
        book = request.env['bookstore.book'].sudo().browse(int(product_id))
        if book.exists():
            # Check stock availability
            if book.stock_quantity < (add_qty if add_qty else set_qty):
                return request.render('bookstore.cart_error', {
                    'error': f'Sorry, only {book.stock_quantity} items available in stock.',
                    'book': book,
                })
        
        return super().cart_update(product_id, add_qty, set_qty, **kw)

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
        """Display detailed view of a single book"""
        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists() or not book.active:
            return request.not_found()
        
        # Get related books from the same category
        related_books = request.env['bookstore.book'].sudo().search([
            ('category_id', '=', book.category_id.id),
            ('id', '!=', book.id),
            ('active', '=', True)
        ], limit=4)
        
        return request.render('bookstore.book_detail', {
            'book': book,
            'related_books': related_books,
        })

    @http.route('/bookstore/category/<int:category_id>', type='http', auth='public', website=True)
    def books_by_category(self, category_id, **kwargs):
        """Display books filtered by category"""
        category = request.env['bookstore.category'].sudo().browse(category_id)
        if not category.exists():
            return request.not_found()
        
        books = request.env['bookstore.book'].sudo().search([
            ('category_id', '=', category_id),
            ('active', '=', True)
        ])
        categories = request.env['bookstore.category'].sudo().search([])
        
        return request.render('bookstore.bookstore_home', {
            'books': books,
            'categories': categories,
            'current_category': category,
        })

    @http.route('/bookstore/search', type='http', auth='public', website=True)
    def book_search(self, search='', **kwargs):
        """Search books by title or author"""
        domain = [('active', '=', True)]
        if search:
            domain.extend([
                '|', '|',
                ('name', 'ilike', search),
                ('author', 'ilike', search),
                ('description', 'ilike', search)
            ])
        
        books = request.env['bookstore.book'].sudo().search(domain)
        categories = request.env['bookstore.category'].sudo().search([])
        
        return request.render('bookstore.bookstore_home', {
            'books': books,
            'categories': categories,
            'search_term': search,
        })
