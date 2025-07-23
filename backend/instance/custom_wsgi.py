"""
Custom WSGI application that auto-initializes Plone site
"""

import os
import sys
from pathlib import Path

# Add instance directory to Python path
instance_dir = Path(__file__).parent
sys.path.insert(0, str(instance_dir))

# Import Zope and our initialization
import Zope2
from initialize_site import initialize_plone_site


class AutoInitializeWSGI:
    """WSGI application that initializes Plone on first request"""
    
    def __init__(self):
        self.initialized = False
        
    def __call__(self, environ, start_response):
        # Initialize on first request
        if not self.initialized:
            print("First request detected, initializing Plone...")
            Zope2.startup()
            app = Zope2.app()
            
            try:
                initialize_plone_site(app)
                import transaction
                transaction.commit()
            except Exception as e:
                print(f"Error during initialization: {e}")
                import transaction
                transaction.abort()
            finally:
                app._p_jar.close()
            
            self.initialized = True
        
        # Handle request normally
        from ZPublisher.WSGIPublisher import publish_module
        return publish_module(environ, start_response)


# Create the application
application = AutoInitializeWSGI()


def make_app(global_conf, zope_conf):
    """Factory for paste.deploy"""
    os.environ['ZOPE_CONF'] = zope_conf
    return application


# For running with waitress directly
if __name__ == '__main__':
    from waitress import serve
    
    print("Starting Plone with auto-initialization...")
    print("Server will be available at http://localhost:8080")
    print("\nThe site will be created automatically on first access.")
    print("CORS is configured from environment variables.")
    
    serve(application, host='0.0.0.0', port=8080)