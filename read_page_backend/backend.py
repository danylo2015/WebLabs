import os
import json
from flask import Flask, jsonify, request, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '/assets'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATA_FILE = os.path.join('read_page_backend', 'data.json')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class Pet:
    def __init__(self, id, name, description, age, price, image):
        self.id = id
        self.name = name
        self.description = description
        self.age = age
        self.price = price
        self.image = image

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'age': self.age,
            'price': self.price,
            'image': self.image
        }

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

def sort_data(data, sort_option):
    if sort_option == "age (low-high)":
        return sorted(data, key=lambda pet: pet['age'])
    elif sort_option == "age (high-low)":
        return sorted(data, key=lambda pet: pet['age'], reverse=True)
    elif sort_option == "price (low-high)":
        return sorted(data, key=lambda pet: pet['price'])
    elif sort_option == "price (high-low)":
        return sorted(data, key=lambda pet: pet['price'], reverse=True)
    elif sort_option == "name (A-Z)":
        return sorted(data, key=lambda pet: pet['name'].lower())
    elif sort_option == "name (Z-A)":
        return sorted(data, key=lambda pet: pet['name'].lower(), reverse=True)
    return data  # Default: return the data unchanged


def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump([pet.to_dict() for pet in data], file, indent=4)


data = [Pet(**pet_data) for pet_data in load_data()]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "Welcome to the CRUD API!"


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/search_and_sort', methods=['POST'])
def search_and_sort_items():
    search_term = request.json.get('search_term', '').lower().replace(' ', '')
    sort_option = request.json.get('sort_option', 'name (A-Z)')
    
    data_dict = load_data()  # Load current data from the JSON file
    filtered_data = [pet for pet in data_dict if search_term in pet['name'].lower().replace(' ', '')]
    sorted_data = sort_data(filtered_data, sort_option)
    
    return jsonify(sorted_data)



@app.route('/count_price', methods=['POST'])
def count_price():
    search_query = request.json.get('query', '').lower().replace(' ', '')
    data = load_data()
    filtered_data = [pet for pet in data if search_query in pet['name'].lower().replace(' ', '')]
    total_price = sum(pet['price'] for pet in filtered_data)
    return jsonify({'total': total_price})


@app.route('/items', methods=['POST'])
def create_item():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
      
        file_url = f'/assets/{filename}'

        new_item_data = request.form.to_dict()
        new_pet = Pet(
            id=len(data) + 1,
            name=new_item_data['name'],
            description=new_item_data['description'],
            age=float(new_item_data['age']),
            price=float(new_item_data['price']),
            image=file_url
        )
        data.append(new_pet)
        sort_option = request.form.get('sort', 'name (A-Z)')  
        sorted_data_dict = sort_data([pet.to_dict() for pet in data], sort_option)  
        sorted_data = [Pet(**pet_dict) for pet_dict in sorted_data_dict]  
        save_data(sorted_data)  
        return jsonify(new_pet.to_dict()), 201
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify([pet.to_dict() for pet in data]), 200

@app.route('/sort', methods=['POST'])
def sort_items():
    sort_option = request.json.get('sort')  
    data_dict = load_data()  
    sorted_data_dict = sort_data(data_dict, sort_option)  
    sorted_data = [Pet(**pet_dict) for pet_dict in sorted_data_dict]  
    save_data(sorted_data)
    return jsonify([pet.to_dict() for pet in sorted_data])  



@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((pet for pet in data if pet.id == item_id), None)
    if item:
        updated_data = request.form.to_dict()
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_url = f'/assets/{filename}'
                item.image = file_url

        item.name = updated_data.get('name', item.name)
        item.description = updated_data.get('description', item.description)
        item.age = float(updated_data.get('age', item.age))
        item.price = float(updated_data.get('price', item.price))

        sort_option = request.form.get('sort', 'name (A-Z)')  
        sorted_data_dict = sort_data([pet.to_dict() for pet in data], sort_option)  
        sorted_data = [Pet(**pet_dict) for pet_dict in sorted_data_dict] 
        save_data(sorted_data)  
        return jsonify(item.to_dict()), 200
        
    else:
        return jsonify({'error': 'Item not found'}), 404

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global data
    data = [pet for pet in data if pet.id != item_id]
    save_data(data)  # Зберегти дані у файл JSON
    return jsonify({'message': 'Item deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)