from application.models import Loan
from application.extensions import ma
from marshmallow import fields




class LoanSchema(ma.SQLAlchemyAutoSchema):
    books = fields.Nested("BookSchema", many=True)
    member = fields.Nested("MemberSchema")
    class Meta:
        model = Loan
        include_fk = True  # This will include member_id foreign key   

class Update_LoanSchema(ma.Schema):
    add_book_ids = fields.List(fields.Int(), required=True)
    remove_book_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_book_ids", "remove_book_ids")

loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)
update_loan_schema = Update_LoanSchema()