from .bookSchema import book_schema, books_schema
from flask import request, jsonify 
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Book, db
from . import books_bp
from application.extensions import limiter, cache
from application.utils.util import encode_token, token_required

from application.blueprints import books




@books_bp.route("/books", methods=["POST"])
def create_book():
    try:
        book_data = book_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    query = select(Book).where(Book.title == book_data['title'])
    existing_book = db.session.execute(query).scalars().all()
    if existing_book:
        return jsonify({"error": "Book already exists."}), 400
    
    new_book = Book(**book_data)
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book), 201


#GET ALL MEMBERS
@books_bp.route("/books", methods=['GET'])
def get_books():

    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get("per_page"))
        query = select(Book)
        books = db.paginate(query,page=page, per_page=per_page )
        return books_schema.jsonify(books),200
    except:
        query = select(Book)
        books = db.session.execute(query).scalars().all()
        return books_schema.jsonify(books)

#GET SPECIFIC BOOK
@books_bp.route("/books/<int:book_id>", methods=['GET'])
def get_book(book_id):
    book = db.session.get(Book, book_id)

    if book:
        return book_schema.jsonify(book), 200
    return jsonify({"error": "Book not found."}), 404

#UPDATE SPECIFIC BOOK
@books_bp.route("/books/<int:book_id>", methods=['PUT'])
def update_book(book_id):
    query = select(Book).where(Book.id == book_id)
    book = db.session.execute(query).scalars().first()

    if not book:
        return jsonify({"error": "Book not found."}), 404
    
    try:
        book_data = book_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in book_data.items():
        setattr(book, field, value)

    db.session.commit()
    return book_schema.jsonify(book), 200

#DELETE SPECIFIC BOOK
@books_bp.route("/books/<int:book_id>", methods=['DELETE'])
@token_required
def delete_book(book_id):
    query = select(Book).where(Book.id == book_id)
    book = db.session.execute(query).scalars().first()
    if not book:
        return jsonify({"error": "Book not found."}), 404
    
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": f'Book id: {book_id}, successfully deleted.'}), 200
    


@books_bp.route("/popular", methods=["GET"])
def popular_books():
    query = select(Book)
    books = db.session.execute(query).scalars().all()

    books.sort(key=lambda book: len(book.loans),reverse=True)

    return books_schema.jsonify(books)


@books_bp.route("/search", methods=["GET"])
def search_book():
    title = request.args.get("title", "")
    

    query = select(Book).where(Book.title.like(f"%{title} %"))
    Books = db.session.execute(query).scalars().all()


    return books_schema.jsonify(books)
