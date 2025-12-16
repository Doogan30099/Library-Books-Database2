from application.models import Order, OrderItems,db
from application.extensions import ma
from marshmallow import fields


class ReciptSchema(ma.Schema):
    '''
    total: 39.02
    order {
        member_id: 1,
        order_date: 2025-01-01,
        order_items: [
            {
                item_id: 1,
                item_name: "Item A",
                item_quantity: 2,
                item_price: 9.99
            },
            {
                item_id: 2,
                item_name: "Item B",
                item_quantity: 1,
                item_price: 19.04
            }
        ]
    }
    '''
    total = fields.Int(required=True)
    order = fields.Nested("OrderSchema", required=True)






class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_relationships = True
    order_items = fields.Nested("OrderItemSchema",exclude=["order_id","item_id","id"], many=True)

class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItems
        item = fields.Nested("ItemSchema", exclude=["id"])


class CreateOrderSchema(ma.Schema):
    '''
    {
        member_id: 1
        item_quantity: [{item_id: 1, item_quantity:3}]

    }
    '''

    member_id = fields.Int(required=True)
    item_quantity = fields.Nested("ItemQuantitySchema", many=True)


class ItemQuantitySchema(ma.Schema):
    item_id = fields.Int(required=True)
    item_quantity = fields.Int(required=True)


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
create_order_schema = CreateOrderSchema
recipt_schema = ReciptSchema()