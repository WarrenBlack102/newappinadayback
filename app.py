from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Card(db.Model):

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    front = db.Column(db.String, unique=False, nullable=False)
    back = db.Column(db.String, unique=False, nullable=False)


    def __init__(self, front, back):
        self.front = front
        self.back = back


class CardSchema(ma.Schema):
    class Meta:
        fields = ('id', 'front', 'back')


card_schema = CardSchema()
multi_card_schema = CardSchema(many=True)

# Endpoint to add a card
@app.route('/card/add', methods=['POST'])
def add_card():
    if request.content_type != 'application/json':
        return jsonify('Error: data MUST be sent as JSON!')

    post_data = request.get_json()
    front = post_data.get('front')
    back = post_data.get('back')

    if front == None:
        return jsonify('Error: Thou Shalt Provide A Value1!')
    if back == None:
        return jsonify('Error: Thou Shalt Provide A Value2!')

    new_record = Card(front, back)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(card_schema.dump(new_record))

# Endpoint to add multiple cards
@app.route('/card/add-multi', methods=['POST'])
def add_multiple_cards():
    if request.content_type != 'application/json':
        return jsonify('Error: You are kind of a putz...the data MUST be sent as JSON!')

    post_data = request.get_json()
    data = post_data.get("data")

    new_records = []

    for card in data:
        front = card.get("front")
        back = card.get("back")

        existing_card_check = db.session.query(Card).filter(Card.front == front).filter(Card.back == back).first()
        if existing_card_check is not None:
            return jsonify("Error: You're trying to add duplicate cards, DING BAT!")
        else:
            new_record = Card(front, back)
            db.session.add(new_record)
            db.session.commit()
            new_records.append(new_record)

    return jsonify(multi_card_schema.dump(new_records))


# Endpoint to query all cards
@app.route('/card/get', methods=['GET'])
def get_all_cards():
    
    all_cards = db.session.query(Card).all()
    return jsonify(multi_card_schema.dump(all_cards))

# Endpoint to query one card
@app.route('/card/get/<id>', methods=['GET'])
def get_card_id(id):
    one_card = db.session.query(Card).filter(Card.id == id).first()
    return jsonify(card_schema.dump(one_card))

# Endpoint to delete a card
@app.route('/card/delete/<id>', methods=['DELETE'])
def card_to_delete(id):
    delete_card = db.session.query(Card).filter(Card.id == id).first()
    
    db.session.delete(delete_card)
    db.session.commit()
    return jsonify("The card you chose is POOF! Gone, done, DELETED!")

# Endpoint to update/edit a card
@app.route('/card/update/<id>', methods=['PUT'])
def update_card_id(id):
    if request.content_type != 'application/json':
        return jsonify('Error: data must be sent as JSON!')

    put_data = request.get_json()
    front = put_data.get('front')
    back = put_data.get('back')

    card_to_update = db.session.query(Card).filter(Card.id == id).first()

    if front != None:
        card_to_update.front = front
    if back != None:
        card_to_update.back = back

    db.session.commit()

    return jsonify(card_schema.dump(card_to_update))

if __name__ == '__main__':
    app.run(debug=True)