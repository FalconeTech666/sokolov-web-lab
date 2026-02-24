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
    
class NewsAdmin(ModelView):
    column_list = ['id', 'title', 'title_en', 'tag', 'image']  # столбцы в таблице
    form_columns = ['title', 'text', 'title_en', 'text_en', 'image', 'tag']  # поля формы
    column_labels = {
        'title': 'Заголовок (RU)',
        'text': 'Текст (RU)',
        'title_en': 'Заголовок (EN)',
        'text_en': 'Текст (EN)',
    }

def setup_admin(app):
    admin = Admin(app, 
                  name='Sokolov Panel',  
                  index_view=SecureAdminIndexView())
    
    admin.add_view(SecureModelView(News, db.session, name="Новости"))
    admin.add_view(SecureModelView(User, db.session, name="Пользователи"))
