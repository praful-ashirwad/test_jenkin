from flask import Flask
from functools import wraps

from ssl import SSLContext

app = Flask(__name__)


def ssl_wrap(app, cert_file, key_file):
    """
    Wraps the WSGI application in an SSL context.

    Args:
        app (WSGIApplication): The WSGI application to wrap.
        cert_file (str): The path to the certificate file.
        key_file (str): The path to the key file.

    Returns:
        A WSGI application that is wrapped in an SSL context.
    """

    context = SSLContext(ssl.PROTOCOL_TLSv1_3)
    context.load_cert_chain(cert_file, key_file)

    def wrapped_app(environ, start_response):
        with context.wrap_socket(
            environ["wsgi.input"], environ["wsgi.output"], environ["wsgi.errors"]
        ) as sock:
            return app(environ, start_response)

    return wrapped_app


def ssl(cert_file, key_file):
    """
    A decorator that enables SSL for a Flask endpoint.

    Args:
        cert_file (str): The path to the certificate file.
        key_file (str): The path to the key file.

    Returns:
        A decorator that can be used to decorate a Flask endpoint.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            with app.app_context():
                app.wsgi_app = ssl_wrap(app.wsgi_app, cert_file, key_file)
                return f(*args, **kwargs)

        return wrapper

    return decorator


@app.route("/secure", methods=["GET"])
@ssl("cert.pem", "key.pem")
def secure():
    return "This route only accepts HTTPS requests."


if __name__ == "__main__":
    app.run()
