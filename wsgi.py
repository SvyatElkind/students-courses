from app import create_app
from app.constants import DEVELOPMENT

app = create_app(DEVELOPMENT)

if __name__ == "__main__":
    app.run()
