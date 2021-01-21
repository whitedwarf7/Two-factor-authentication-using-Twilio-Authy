from flask import Flask,render_template,request,jsonify
from authy.api import AuthyApiClient
from flask_sqlalchemy import SQLAlchemy


app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


class User(db.Model):
    userid=db.Column(db.String(30),primary_key=True)
    password=db.Column(db.String(30))

db.create_all()
authy_api = AuthyApiClient('API Token')
user = authy_api.users.create(
    email='ghmelkunde@gmail.com',
    phone='xxxxxxxxxx',
    country_code=+91)

if user.ok():
    authy_id = user.id
    print(user.id)
else:
    print(user.errors())


@app.route('/',methods=["GET"])
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def log_in():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if User.query.get(username):
            user=User.query.get(username)
            if user.userid == username:
                if user.password == password:

                    sms = authy_api.users.request_sms(339090247)
                    return render_template('verify.html',dummy="Correct Password")
                else:
                    return render_template('login.html',dummy="wrong Password")
            else:
                return render_template('login.html',dummy="No user found")
        else:
            return render_template('login.html',dummy="Not Registered")
    else:
        return render_template('login.html')

@app.route('/verify',methods=['POST'])
def verify():
    authy_id=339090247
    token=request.form['smscode']
    try :
        verification = authy_api.tokens.verify(authy_id, token=int(token))
        if verification.ok():
            return render_template("welcome.html",user=f"Welcome logged in successufully")
        else:
            return render_template("login.html",message=f"Wrong OTP try again")
    except ValueError:
        return render_template("login.html",message=f"Otp must be numeric")

@app.route('/create',methods=['POST','GET'])
def create():
    if request.method=="GET":
        return render_template("createuser.html")
    else:
        uid=request.form['username']
        upass=request.form['password']
        if User.query.get(uid):
            return jsonify({"message":"already exists"})
        else:
            new_user=User(userid=uid,password=upass)
            db.session.add(new_user)
            db.session.commit()
            return render_template("home.html",message=f"{new_user.userid} created successufully ")


if __name__=="__main__":
    app.run(port=8060,debug=True)
