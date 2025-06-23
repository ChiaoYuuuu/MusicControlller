from django.contrib.auth import authenticate

class AuthService:
    @staticmethod
    def validate_login(username, password):
        if not username or not password:
            return None, 'Username and password required'
        return {'username': username, 'password': password}, None

    @staticmethod
    def validate_register(username, password):
        if not username or not password:
            return None, 'Username and password are required'
        return {'username': username, 'password': password}, None

    @staticmethod
    def login(username, password):
        if not username or not password:
            return None, 'Username and password required'
        user = authenticate(username=username, password=password)
        if user is not None:
            return {
                'user_id': user.id,
                'username': user.username
            }, None
        else:
            return None, 'Invalid credentials'

    @staticmethod
    def register(username, password):
        if not username or not password:
            return None, 'Username and password are required'
        try:
            user = User.objects.create_user(username=username, password=password)
            return {
                "message": "User registered successfully",
                "user_id": user.id,
                "username": user.username
            }, None
        except IntegrityError:
            return None, 'Username already exists'
        except Exception:
            return None, 'Internal server error' 