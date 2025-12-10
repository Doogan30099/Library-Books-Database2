from application.models import db, Book, Loan
from sqlalchemy import select, delete
from marshmallow import ValidationError
from application.blueprints.loans import loans_bp
from .loanSchemas import loan_schema, loans_schema, return_loan_schema, update_loan_schema
from flask import request, jsonify




@loans_bp.route("/loans", methods=["POST"])
def create_loan():
    try:
        loan_data = loan_schema.load(request.json)
        print(loan_data)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    new_loan = Loan(loan_date = loan_data['loan_date'], member_id = loan_data['member_id'])

    for book_id in loan_data["book_ids"]:
        query = select(Book).where(Book.id == book_id)
        book = db.session.execute(query).scalar()
        if book:
            new_loan.books.append(book)
        else:
            return jsonify({"error": f"Book with id {book_id} not found."}), 404
    
    db.session.add(new_loan)
    db.session.commit()
    return loan_schema.jsonify(new_loan), 201

#GET ALL LOANS
@loans_bp.route("/loans", methods=['GET'])
def get_loans():
    query = select(Loan)
    result = db.session.execute(query).scalars().all()
    return loans_schema.jsonify(result), 200


#Delete a specific loan
@loans_bp.route("/loans/<int:loan_id>", methods=['DELETE'])
def delete_loan(loan_id):
    query = select(Loan).where(Loan.id == loan_id)
    loan = db.session.execute(query).scalars().first()

    if not loan:
        return jsonify({"error": "Loan not found."}), 404
    
    db.session.delete(loan)
    db.session.commit()
    return jsonify({"message": f'Loan id: {loan_id}, successfully deleted.'}), 200



#Update a specific loan
@loans_bp.route("/loans/<int:loan_id>", methods=['PUT'])
def update_loan(loan_id):
    try:
        loan_updates = update_loan_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    
    query = select(Loan).where(Loan.id == loan_id)
    loan = db.session.execute(query).scalars().first()

    for book_id in loan_updates['add_book_ids']:
       query = select(Book).where(Book.id == book_id)
       book = db.session.execute(query).scalars().first()
       if book and book not in loan.books:
           loan.books.append(book)

    for book_id in loan_updates['remove_book_ids']:
       query = select(Book).where(Book.id == book_id)
       book = db.session.execute(query).scalars().first()
       if book and book in loan.books:
           loan.books.remove(book)

    db.session.commit()
    return loan_schema.jsonify(loan), 200

