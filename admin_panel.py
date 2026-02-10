from flask import redirect, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from models import News, User, db

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.login == 'sokolovmslu'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login')) 

class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.login == 'sokolovmslu'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

def setup_admin(app):
    admin = Admin(app, 
                  name='Sokolov Panel', 
                  template_mode='bootstrap3', 
                  index_view=SecureAdminIndexView())
    
    admin.add_view(SecureModelView(News, db.session, name="Новости"))
    admin.add_view(SecureModelView(User, db.session, name="Пользователи"))
