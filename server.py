from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime

class Contacts:
    def __init__(self):
        self.__my_conn = sqlite3.connect('db/contacts.db')
        self.__my_curr = self.__my_conn.cursor()
    
    def put_data(self, name:str, number:int) -> None:
        self.__my_curr.execute(f'insert into identity values ("{name}", {number})')
        self.__my_conn.commit()

    def get_all_data(self) -> list:
        self.__my_curr.execute('select * from identity')
        return self.__my_curr.fetchall()
    
    def get_data_from_name(self, name:str) -> int:
        self.__my_curr.execute(f'select number from identity where name="{name}"')
        return self.__my_curr.fetchone()
    
    def delete_data_from_name(self, name:str) -> None:
        self.__my_curr.execute(f'delete from identity where name="{name}"')
        self.__my_conn.commit()

    def update_data(self, name:str, number:int) -> None:
        self.__my_curr.execute(f'update identity set number={number} where name="{name}"')
        self.__my_conn.commit()

    def close_connection(self) -> None:
        self.__my_conn.close()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'GET':
        obj = Contacts()
        all_data = obj.get_all_data()
        obj.close_connection()

        return render_template('index.html', all_data=all_data)

    elif request.method == 'POST':
        name = request.form.get('name')
        number = request.form.get('number')
        obj = Contacts()
        obj.put_data(name, number)
        obj.close_connection()

        return redirect('/')

@app.route('/delete/<string:name>')
def delete_data(name):  
    obj = Contacts()
    obj.delete_data_from_name(name)
    obj.close_connection()

    return redirect('/')

@app.route('/update/<string:name>', methods=['GET', 'POST'])
def update_data(name):
    if request.method == 'GET':
        obj = Contacts()
        number = obj.get_data_from_name(name)[0]
        obj.close_connection()

        return render_template('update.html', name=name, number=number)
    
    elif request.method == 'POST':
        number = request.form.get('number')
        obj = Contacts()
        obj.update_data(name, number)
        obj.close_connection()

        return redirect('/')

@app.route('/api')
def func_name():
    name = request.args.get('name', default=None, type=str)
    obj = Contacts()

    if name == 'all':
        all_data = obj.get_all_data()
        result = {}
        result['All'] = []
        for name, number in all_data:
            result['All'].append({'Name': name, 'Number': number, 'Date': datetime.now()})

    elif (name is None) or (obj.get_data_from_name(name) is None):
        result = {
        'Name': 'Not Found',
        'Date': datetime.now()
        }

    else:
        number = obj.get_data_from_name(name)[0]
        result = {
        'Name': name,
        'Number': number,
        'Date': datetime.now()
        }
    
    obj.close_connection()    
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')