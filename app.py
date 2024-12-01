from flask import Flask,redirect,render_template,flash,url_for,request
from flask_sqlalchemy import SQLAlchemy

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_login import UserMixin,LoginManager,current_user,login_user,logout_user,login_required

from PIL import Image
from datetime import datetime

from io import BytesIO
import os
import numpy as np

import pickle

app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/')

admin = Admin()

login_manager = LoginManager()

db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'mysecret'

db.init_app(app)

admin.init_app(app)
login_manager.init_app(app)

class User(db.Model,UserMixin):

    id = db.Column(db.Integer,primary_key=True)

    def __repr__(self):
        return f'{id}'

class Form(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)

    image_class = db.Column(db.String,nullable=False)
    accuracy = db.Column(db.Double,nullable=False)
    
    date = db.Column(db.Date, default=datetime.now())
    
    def __repr__(self):
        return f'{self.id} --> {self.name}'

@login_manager.user_loader
def login(user_id):
    return User.query.get(user_id)

class View(ModelView):
    def is_accessible(self):
        return False

class UserView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_calback(self,name,**kwargs):
        return redirect(url_for('login'))

    can_create = True
    can_delete = True
    can_edit = True
    can_view_details = True
    can_export = True
    column_display_actions = True
    column_list = ['id','accuracy','image_class','date']

admin.add_view(UserView(Form, db.session))

admin.add_view(View(User, db.session))

with app.app_context():
    db.create_all()

with open('model.pkl','rb') as file:
    model = pickle.load(file)

class_indicies = dict()
classes = list(os.listdir('train'))

for i, v in enumerate(classes):
    class_indicies[i] = v

@app.route('/',methods=['POST','GET'])
def main():
    if request.method == 'POST':
        image = request.files['image']

        if image.filename == '':
            flash('No Image Uploaded!')
            return redirect(url_for('main'))
        
        read_img = image.read()
        
        img = Image.open(BytesIO(read_img))
        img = img.resize((256,256))

        img = np.array(img)
        
        img = img / 255.0
        img = np.expand_dims(img,axis=0)

        result = model.predict(img)

        acc = np.max(result)
        result = np.argmax(result)

        class_name = class_indicies[result]

        new_data = Form(image_class = class_name, accuracy = acc)
        
        db.session.add(new_data)
        db.session.commit()

        flash('Data added successfully to database!')

        return render_template('base.html',class_indicies=class_indicies,class_name=class_name,accuracy=acc)
        


    return render_template('base.html',class_indicies=class_indicies,class_name=None)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/admin')
    
    if request.method == 'POST':
        password = request.form['password']

        if password == '12345':
            user = User.query.get(1)
            login_user(user)
            
            flash('logged in successfully!!')
            return redirect('/admin')

    return render_template('login.html')

@app.route('/logout')
@login_required

def logout():

    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(error):
    return "<center><h1>Wrong url !!!</h1></center>"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
