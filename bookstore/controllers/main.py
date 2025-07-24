# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class BookstoreController(http.Controller):

    @http.route('/bookstore/test', type='http', auth='public', website=True)
    def bookstore_test(self, **kwargs):
        """Simple test page to verify routing works"""
        return request.render('bookstore.bookstore_test', {})

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, **kwargs):
        """Display all books on the bookstore homepage"""
        try:
            books = request.env['bookstore.book'].sudo().search([('active', '=', True)])
            categories = request.env['bookstore.category'].sudo().search([])
            
            # Try to get featured books, but fallback if field doesn't exist
            try:
                featured_books = request.env['bookstore.book'].sudo().search([
                    ('active', '=', True),
                    ('featured', '=', True),
                    ('stock_quantity', '>', 0)
                ], limit=6)
            except:
                featured_books = []
            
            return request.render('bookstore.bookstore_home', {
                'books': books,
                'categories': categories,
                'featured_books': featured_books,
            })
        except Exception as e:
            # Fallback if there's an issue
            return request.render('bookstore.bookstore_simple', {
                'error': str(e)
            })

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
        """Display detailed view of a single book"""
        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists() or not book.active:
            return request.not_found()
        
        # Get related books from the same category (basic version)
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
        """Search books by title, author, ISBN, or description"""
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

    # Temporarily disabled until fields are migrated
    # @http.route('/bookstore/filter/<string:filter_type>', type='http', auth='public', website=True)
    # def filter_books(self, filter_type, **kwargs):
    #     """Filter books by specific criteria"""
    #     domain = [('active', '=', True)]
    #     
    #     if filter_type == 'available':
    #         domain.append(('stock_quantity', '>', 0))
    #     elif filter_type == 'featured':
    #         domain.append(('featured', '=', True))
    #     elif filter_type == 'new':
    #         domain.append(('condition', '=', 'new'))
    #     elif filter_type == 'ebook':
    #         domain.append(('book_format', '=', 'ebook'))
    #     elif filter_type == 'hardcover':
    #         domain.append(('book_format', '=', 'hardcover'))
    #     
    #     books = request.env['bookstore.book'].sudo().search(domain, order='name')
    #     categories = request.env['bookstore.category'].sudo().search([('active', '=', True)], order='display_order, name')
    #     
    #     return request.render('bookstore.bookstore_home', {
    #         'books': books,
    #         'categories': categories,
    #         'current_filter': filter_type,
    #     })
    
    # Temporarily disabled until fields are migrated  
    # @http.route('/bookstore/api/book/<int:book_id>/info', type='json', auth='public')
    # def book_info_api(self, book_id, **kwargs):
    #     """API endpoint for book information"""
    #     try:
    #         book = request.env['bookstore.book'].sudo().browse(book_id)
    #         
    #         if not book.exists() or not book.active:
    #             return {'error': 'Book not found'}
    #         
    #         return {
    #             'id': book.id,
    #             'name': book.name,
    #             'author': book.author,
    #             'price': book.price,
    #             'stock_quantity': book.stock_quantity,
    #             'is_available': book.is_available,
    #             'category': book.category_id.name if book.category_id else None,
    #             'description': book.description,
    #             'book_format': dict(book._fields['book_format'].selection).get(book.book_format),
    #             'condition': dict(book._fields['condition'].selection).get(book.condition),
    #             'isbn': book.isbn,
    #             'publisher': book.publisher,
    #             'pages': book.pages,
    #         }
    #         
    #     except Exception as e:
    #         return {'error': str(e)}
    
    # Temporarily disabled until fields are migrated
    # @http.route('/bookstore/api/categories', type='json', auth='public')
    # def categories_api(self, **kwargs):
    #     """API endpoint for categories"""
    #     try:
    #         categories = request.env['bookstore.category'].sudo().search([('active', '=', True)], order='display_order, name')
    #         
    #         return [{
    #             'id': cat.id,
    #             'name': cat.name,
    #             'book_count': cat.book_count,
    #             'description': cat.description,
    #         } for cat in categories]
    #         
    #     except Exception as e:
    #         return {'error': str(e)}
