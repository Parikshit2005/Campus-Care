from flask import Flask
from config import Config
from models import db, bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from auth.routes import auth
app.register_blueprint(auth, url_prefix='/auth')

from main.routes import main
app.register_blueprint(main)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)