from modules.home import home_bp

def route(app):
    app.register_blueprint(home_bp)
    
