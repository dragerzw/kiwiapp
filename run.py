import os

from app import create_app
from app.config import config

# Use 'development' by default
env = os.environ.get('FLASK_ENV', 'development')
config_class = config.get(env, config.get('development'))
app = create_app(config_class)

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=bool(getattr(config_class, 'DEBUG', False)),
        use_reloader=False,
    )
