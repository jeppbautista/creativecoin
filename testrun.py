import os


if __name__ == "__main__":
    os.environ['FLASK_APP']='creativecoin/__init__.py'
    os.environ['FLASK_ENV']='development'
    os.environ['SERVER_NAME']='localhost:5000'
    os.environ['SECRET_KEY']='D9D7799EFE4327C64A6FF30FBDE865DFA5C45D4BC8265AD7E79205F13CDBA8BF'
    os.environ['PASSWORD']='CCcsbn7270$$$'
    os.environ['GOOGLE_CLIENT_ID']='844772594291-evimb3tfp5nqhdlu1cqub98p8m37vlqd.apps.googleusercontent.com'
    os.environ['GOOGLE_CLIENT_SECRET']='ZQTYP7VjHMV5fnxNP9k-fRFz' 
    os.environ['OAUTHLIB_INSECURE_TRANSPORT']='1'
    from creativecoin import app

    app.run(host='localhost')