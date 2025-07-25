# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class BookstoreController(http.Controller):

    @http.route('/bookstore', type='http', auth='public', website=True)
    def bookstore_home(self, **kwargs):
        books = request.env['bookstore.book'].sudo().search([('is_published', '=', True)])
        
        return request.render('bookstore.bookstore_home', {
            'books': books,
        })

    @http.route('/bookstore/book/<int:book_id>', type='http', auth='public', website=True)
    def book_detail(self, book_id, **kwargs):
        book = request.env['bookstore.book'].sudo().browse(book_id)
        if not book.exists() or not book.is_published:
            return request.not_found()
        
        return request.render('bookstore.book_detail', {
            'book': book,
        })
