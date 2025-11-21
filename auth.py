# ---------- Auth helpers (based on your code) ----------


def encode_jwt(user_id):
    payload = {

        'user_id': user_id,

        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6)

    }

    return jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')


def decode_jwt(token):
    try:

        return jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])

    except Exception:

        return None


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        token = request.cookies.get('jwt') or request.headers.get('Authorization')

        if token and token.startswith('Bearer '):
            token = token.split(' ', 1)[1]

        payload = decode_jwt(token) if token else None

        if not payload or not payload.get('user_id'):
            return jsonify({'message': 'Token invalid or missing'}), 401

        g.user_id = payload['user_id']

        return f(*args, **kwargs)

    return wrapper

# ---------- Auth routes (signup/login/logout) ----------

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}

    username = data.get('username')

    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = User(username=username, password=hashed)

    db.session.add(user)

    db.session.commit()

    return jsonify({'message': 'User registered'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    username = data.get('username')

    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = encode_jwt(user.id)

    resp = make_response({'message': 'Login successful'})

    resp.set_cookie('jwt', token, httponly=True, samesite='Strict')

    return resp


@app.route('/logout', methods=['POST'])
def logout():
    resp = make_response(jsonify({'message': 'Logged out'}))

    resp.set_cookie('jwt', '', expires=0, httponly=True, samesite='Strict')

    return resp
