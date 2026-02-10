from flask import session, redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models import News, User, db

class SecureModelView(ModelView):
    def is_accessible(self):
        return 'login' in session and session['login'] == 'sokolovmslu'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login')) 

class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return 'login' in session and session['login'] == 'sokolovmslu'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

def setup_admin(app):
    admin = Admin(app, 
                  name='Sokolov Panel', 
                  template_mode='bootstrap3', 
                  index_view=SecureAdminIndexView())
    
    admin.add_view(SecureModelView(News, db.session, name="Новости"))
    admin.add_view(SecureModelView(User, db.session, name="Пользователи"))