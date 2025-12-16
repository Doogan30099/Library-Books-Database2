from application.models import db, Order, OrderItems 
from sqlalchemy import select, delete
from marshmallow import ValidationError
from application.blueprints.orders import orders_bp
from .OrderSchemas import order_schema, orders_schema,create_order_schema, recipt_schema
from flask import request, jsonify
from datetime import date



@orders_bp.route("/" , methods=["POST"])
def create_order():
    try:
        order_data = create_order_schema.load(request.json)
        print(order_data)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(member_id=order_data['member_id'], order_date=date.today)

    db.session.add(new_order)
    db.session.commit()


    for item in order_data['item_quantity']:
        order_item = OrderItems(order_id=new_order.id, item_id=item['item_id'], item_quantity=item['item_quantity'])
        db.session.add(order_item)

    db.session.commit()
    total = 0
    for item in new_order.order_items:
        price = item.quantity * item.item.price
        total += price

    recipt = {
        "total": total,
        "order": new_order
    }

    return recipt_schema.jsonify(recipt), 201