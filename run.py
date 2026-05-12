from app import create_app
from app.config import config
import os

# Use 'development' by default
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(config.get(env))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
