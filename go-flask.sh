pid=$(ps aux | grep 'flask' | awk '{print $2}') ;
kill -9 $pid;
source venv/bin/activate;
export FLASK_APP=creativecoin/__init__.py
export FLASK_ENV=development;
export SERVER_NAME=localhost:5000;
export SECRET_KEY=D9D7799EFE4327C64A6FF30FBDE865DFA5C45D4BC8265AD7E79205F13CDBA8BF
export PASSWORD='CCcsbn7270$$$'
export GOOGLE_CLIENT_ID=844772594291-evimb3tfp5nqhdlu1cqub98p8m37vlqd.apps.googleusercontent.com
export GOOGLE_CLIENT_SECRET=ZQTYP7VjHMV5fnxNP9k-fRFz 
export OAUTHLIB_INSECURE_TRANSPORT=1

flask run --host=0.0.0.0