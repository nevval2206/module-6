app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', 'dev-secret')

db = SQLAlchemy(app)
