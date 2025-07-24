# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class BookstoreController(http.Controller):

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, **kwargs):
        """Display all books on the bookstore homepage"""
        books = request.env['bookstore.book'].sudo().search([('active', '=', True)])
        categories = request.env['bookstore.category'].sudo().search([])
        
        return request.render('bookstore.bookstore_home', {
            'books': books,
            'categories': categories,
        })

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
