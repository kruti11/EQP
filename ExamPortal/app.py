from flask import Flask,render_template,redirect,session,request,url_for
from flask.helpers import total_seconds
from flaskext.mysql import MySQL
from pymysql import NULL

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'truptisql_1198'
app.config['MYSQL_DATABASE_DB'] = 'qems'

mysql=MySQL(app)
mysql.init_app(app)


s_time = "06/29/2021 22:30:30"
end_time = "11/11/2021 00:00:30"

def numQues():
    conn=mysql.connect()
    cur=conn.cursor()
    cur.execute("select count(*) from questions;")
    data=cur.fetchone()
    cur.close()
    return data




@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']

        cur=mysql.connect().cursor()
        cur.execute("select * from users where email='"+email+"' ")
        user=cur.fetchone()
        
        cur.close()
        print("hey")
        #if user > 0:
        if password == user[3]:
            print("hello")
            session['name']=user[0]
            session['lname']=user[1]
            session['email']=user[2]
            session['username']=user[6]
            session['user_marks']=0
            session['i']=1

            return render_template("home.html")

        else:
            return "Please enter Correct password again"

        # else:
        #     return "error User not found"
    else:
        return render_template('login.html')

      

@app.route('/register',methods=["GET","POST"])
def register():
    if request.method=='GET':
        return render_template("register.html")
    else:
        fname=request.form['first_name']
        lname=request.form['last_name']
        email=request.form['email']
        password=request.form['password']
        gender=request.form['gender']
        dob=request.form['birthday']
        username=request.form['username']
        phone=request.form['phone']

        conn=mysql.connect()
        cur=conn.cursor()
        cur.execute("INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(fname,lname,email,password,gender,dob,username,phone))
        cur.execute("INSERT INTO leaderboard(username) VALUES (%s)",(username))
    
        conn.commit()
        cur.close()
        session['fname']=request.form['first_name']
        session['email']=request.form['email']
        return redirect(url_for('login'))


@app.route('/instructions',methods=["GET","POST"])
def instruction():
    total_Q=numQues()
    print("G")
    for k in range(1,total_Q[0]+1):
        print(k)
        l=str(k)
        session[l]=0
    return render_template("instructions.html",sTime=s_time,eTime=end_time,total_Q=total_Q[0])

@app.route('/proflogin',methods=["GET","POST"])
def proflogin():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']

        if email == "prof@admin.com" and password=="password":
            session['prof']=1
            return redirect(url_for('profportal'))
        else:
            return "Error in password or email mismatch"
    else:
        return render_template('proflogin.html')


@app.route('/profportal',methods=["GET","POST"])
def profportal():
    total_Q=numQues()
    session['q']=total_Q[0]+1
    if request.method=='POST':
        q_no=request.form['q_no']
        question=request.form['question']
        a = request.form['A']
        b = request.form['B']
        c = request.form['C']
        d = request.form['D']
        correct_option = request.form['Correct_answer']
        marks = request.form['marks']

        conn = mysql.connect()
        cur = conn.cursor()

        query="insert into questions values('{}','{}','{}','{}','{}','{}','{}','{}')".format(q_no,question,a,b,c,d,correct_option,marks)
        cur.execute(query)
        conn.commit()
        cur.close()
        return render_template("quesportal.html",total=total_Q[0]+2)
    else:
        return render_template("quesportal.html",total=total_Q[0]+1)


@app.route('/signout',methods=["GET","POST"])
def signout():
    session.clear()
    return render_template("home.html")

@app.route('/profsignout')
def profsignout():
    session['prof']=0
    return redirect(url_for('home'))


@app.route('/questions',methods=["GET","POST"])
def questions():
    global s_time
    global end_time
    total_Q=numQues()

    if request.method=='POST':
        opt=request.form['option']
        conn=mysql.connect()
        cur=conn.cursor()
        query="select correct_answer,marks from questions WHERE q_no='{}'".format(session['i'])
        cur.execute(query)
        x=cur.fetchone()
        conn.commit()
        cur.close()

        k=str(session['i'])

        if opt==x[0] and session[k]==0:
            session['user_marks']=session['user_marks']+x[1]
            session[k]=1
        if opt != x[0] and session[k] == 1 :
            session['user_marks'] = session['user_marks'] - x[1]
            session[k] = 0

        return render_template("question.html",s_time,eTime = end_time,total_Q=total_Q[0])
    else:

        cur = mysql.connect().cursor()
        query="SELECT q_no,question,a,b,c,d,marks FROM questions WHERE q_no='{}'".format(session['i'])
        cur.execute(query)
        data = cur.fetchone()
        cur.close()
        print("hhh")

    if data != NULL:
        print("ttt")
        session['q_no']=data[0]
        session['Q']=data[1]
        session['A']=data[2]
        session['B']=data[3]
        session['C']=data[4]
        session['D']=data[5]
        session['q_mark']=data[6]
    return render_template("question.html",sTime = s_time,eTime = end_time,total_Q=total_Q[0])

@app.route('/next')
def Next():
    total_Q=numQues()
    if session['i'] == total_Q[0]:
        return redirect(url_for('questions'))
    else:
        session['i']=session['i']+1
    return redirect(url_for('questions'))

@app.route('/prev')
def prev():
    global i
    if session['i']==1:
        return redirect(url_for('questions'))
    else:
        session['i']=session['i']-1
    return redirect(url_for('questions'))

@app.route('/final_submit')
def final_submit():
    global user_marks
    session['i']=1
    conn=mysql.connect()
    cur=conn.cursor()
    query="select marks from questions;"
    cur.execute(query)
    x=cur.fetchall()
    conn.commit()
    cur.close()

    conn=mysql.connect()
    cur=conn.cursor()
    query1="update leaderboard set marks='{}' where username='{}';".format(session['user_marks'],session['username'])
    cur.execute(query1)
    conn.commit()
    cur.close()

    y=list(sum(x,()))
    print(y)
    y=[int(h) for h in y]
    total_marks=sum(y)
    session['total_marks']=total_marks
    user_marks=0
    return render_template("result.html",res=total_marks)

@app.route('/results')
def results():
    return render_template("result.html")

@app.route('/profview',methods=["GET","POST"])
def profview():
    if request.method == 'GET' :
        conn = mysql.connect()
        cur = conn.cursor()
        query="select q_no,question,a,b,c,d,correct_answer,marks from questions;"
        cur.execute(query)
        Qdata = cur.fetchall()
        conn.commit()
        cur.close()
        return render_template('profview.html',Qdata=Qdata)
    else :
        return render_template('profview.html')

@app.route('/edit_q',methods=["POST"])
def edit_q():
    q_no = request.form['edit']

    conn = mysql.connect()
    cur = conn.cursor()
    query="select question,a,b,c,d,correct_answer,marks from questions where q_no='{}';".format(q_no)
    cur.execute(query)
    Qdata = cur.fetchone()
    conn.commit()
    cur.close()

    return render_template("edit.html",total=q_no,Qdata=Qdata)

@app.route('/edit',methods=["POST"])
def edit():
    q_no = request.form['q_no']
    question = request.form['question']
    a = request.form['A']
    b = request.form['B']
    c = request.form['C']
    d = request.form['D']
    correct_option = request.form['Correct_answer']
    marks = request.form['marks']

    conn = mysql.connect()
    cur = conn.cursor()
    query="UPDATE questions SET question = '{}',a='{}',b='{}',c='{}',d='{}',correct_answer='{}',marks='{}' where q_no='{}';".format(question,a,b,c,d,correct_option,marks,q_no)
    cur.execute(query)
    conn.commit()
    cur.close()
    return redirect(url_for('profview'))


@app.route('/delete_q',methods=["POST"])
def delete():
    q_no = request.form['delete']

    conn = mysql.connect()
    cur = conn.cursor()
    query="Update questions set question=NULL,a=NULL,b=NULL,c=NULL,d=NULL,correct_answer=NULL,marks=0 where q_no='{}';".format(q_no)
    cur.execute(query)
    conn.commit()
    cur.close()
    return redirect(url_for('profview'))

@app.route('/rankings')
def leaderboard():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("select username,marks,fname,lname from leaderboard natural join users where username = username order by marks desc;")
    Ldata = cur.fetchall()
    conn.commit()
    cur.close()
    print(Ldata)
    size = len(Ldata)

    List1 = []
    for i,_ in enumerate(Ldata):
        List1.append(Ldata[i] + (i+1,)) 

    return render_template('ranking.html',data=List1)       

@app.route('/reset_lb',methods=["POST"])
def clear_lb():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("update leaderboard set marks=0;")
    conn.commit()
    cur.close()
    return "success"

@app.route('/test_timings',methods=["POST","GET"])
def test_timings():
    global s_time
    global end_time

    if request.method == 'POST':
        s_time = request.form['s_time']
        end_time = request.form['end_time']

        return render_template("set_time.html",sTime = s_time,eTime = end_time)
    else :
        return render_template("set_time.html",sTime = s_time,eTime = end_time)      
        

@app.route('/prohibited')
def prohibited():
    global s_time
    return render_template("prohibited.html",sTime = s_time)





if __name__ == "__main__":
    app.secret_key = "trupen"
    app.run(debug=True)