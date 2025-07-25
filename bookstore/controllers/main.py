# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class BookstoreController(http.Controller):

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, **kwargs):
        """Bookstore homepage"""
        try:
            books = request.env['bookstore.book'].sudo().search([])
            categories = request.env['bookstore.category'].sudo().search([])
            
            return request.render('bookstore.bookstore_home', {
                'books': books,
                'categories': categories,
            })
        except Exception as e:
            return request.render('website.404')

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
        """Book detail page"""
        try:
            book = request.env['bookstore.book'].sudo().browse(book_id)
            if not book.exists():
                return request.render('website.404')
            
            return request.render('bookstore.book_detail', {
                'book': book,
            })
        except Exception as e:
            return request.render('website.404')
