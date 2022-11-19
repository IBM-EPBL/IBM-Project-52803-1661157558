import email
from flask import Flask ,render_template,request,redirect,url_for,session,flash

import re


import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=0c77d6f2-5da9-48a9-81f8-86b520b87518.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31198;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=jsl71809;PWD=bl03j1eFRYzVCv4R",'','')

app = Flask(__name__)
app.secret_key = 'qwdqwjdjecnwj'




@app.route('/')
def home():
    return render_template('home.html')

@app.route("/home")
def homepage():
    return render_template("homepage.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        Password = request.form['password']
        sql = "SELECT * FROM user WHERE name=?"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, name)
        ibm_db.execute(prep_stmt)
        account = ibm_db.fetch_assoc(prep_stmt)
        print(account)
        if account:
            error = "Account already exists! Log in to continue !"
        else:
            insert_sql = "INSERT INTO user values(?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, Password)
            ibm_db.execute(prep_stmt)
    return render_template('login.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password)
        sql = "SELECT * FROM user WHERE email=? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
          session['Loggedin'] = True
          session['email'] = account['EMAIL']
          return render_template('homepage.html')

        else:
          error = "Incorrect username / password"
    return render_template('login.html')

#ADDING----DATA


@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    date = request.form['date']
    expense_name = request.form['expense_name']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    insert_sql = 'INSERT INTO expenses (date,expense_name,amount,paymode,category) VALUES (?,?,?,?,?)'
    pstmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(pstmt, 1, date)
    ibm_db.bind_param(pstmt, 2, expense_name)
    ibm_db.bind_param(pstmt, 3, amount)
    ibm_db.bind_param(pstmt, 4, paymode)
    ibm_db.bind_param(pstmt, 5, category)
    ibm_db.execute(pstmt)


          
    return redirect("/display.html")

#DISPLAY---graph 


@app.route("/display")
def display():
    print(session["username"],session['id'])
    sql = 'SELECT * FROM expenses WHERE userid = % s AND date ORDER BY `expenses`.`date` DESC',(str(session['id']))
    prep_stmt = ibm_db.prepare(conn, sql)
    expense = ibm_db.fetchall()
  
       
    return render_template('display.html' ,expense = expense)
 
#delete---the--data

@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
     sql = 'DELETE FROM expenses WHERE  id = {0}'.format(id)
     prep_stmt = ibm_db.prepare(conn, sql)
     ibm_db.execute()
     print('deleted successfully')    
     return redirect("/display")

#UPDATE---DATA

@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    sql = 'SELECT * FROM expenses WHERE  id = %s', (id,)
    prep_stmt = ibm_db.prepare(conn, sql)
    row = ibm_db.fetchall()
   
    print(row[0])
    return render_template('edit.html', expenses = row[0])


@app.route('/update/<id>', methods = ['POST'])
def update(id):
  if request.method == 'POST' :
   
      date = request.form['date']
      expense_name = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']
      sql = "UPDATE `expenses` SET `date` = % s , `expensename` = % s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`id` = % s ",(date, expense_name, amount, str(paymode), str(category),id)
      prep_stmt = ibm_db.prepare(conn, sql)
      ibm_db.execute()
      print('successfully updated')
      return redirect("/display")
    

#limit
@app.route("/limit" )
def limit():
       return redirect('/limitn')

@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
        number= request.form['number']
        sql = 'INSERT INTO limits VALUES (NULL, % s, % s) ',(session['id'], number)
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute()

        return redirect('/limitn')

@app.route("/limitn") 
def limitn():
    sql = 'SELECT limitss FROM `limits` ORDER BY `limits`.`id` DESC LIMIT 1'
    prep_stmt = ibm_db.prepare(conn, sql)
    x= ibm_db.fetchone()
    s = x[0]
    
    
    return render_template("limit.html" , y= s)


#REPORT

@app.route("/today")
def today():
      sql = 'SELECT TIME(date)   , amount FROM expenses  WHERE userid = %s AND DATE(date) = DATE(NOW()) ',(str(session['id']))
      prep_stmt = ibm_db.prepare(conn, sql)
      texpense = ibm_db.cursor.fetchall()
      print(texpense)
      
      sql = 'SELECT * FROM expenses WHERE userid = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id']))
      prep_stmt = ibm_db.prepare(conn, sql)
      expense = ibm_db.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
 
  
@app.route("/month")
def month():
      sql = 'SELECT DATE(date), SUM(amount) FROM expenses WHERE userid= %s AND MONTH(DATE(date))= MONTH(now()) GROUP BY DATE(date) ORDER BY DATE(date) ',(str(session['id']))
      prep_stmt = ibm_db.prepare(conn, sql)
      texpense = ibm_db.fetchall()
      print(texpense)
      
      sql = 'SELECT * FROM expenses WHERE userid = % s AND MONTH(DATE(date))= MONTH(now()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id']))
      prep_stmt = ibm_db.prepare(conn, sql)
      expense = ibm_db.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
 
@app.route("/year")
def year():
      sql = 'SELECT MONTH(date), SUM(amount) FROM expenses WHERE userid= %s AND YEAR(DATE(date))= YEAR(now()) GROUP BY MONTH(date) ORDER BY MONTH(date) ',(str(session['id']))
      texpense = ibm_db.fetchall()
      print(texpense)
      
    
      sql = 'SELECT * FROM expenses WHERE userid = % s AND YEAR(DATE(date))= YEAR(now()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id']))
      expense = ibm_db.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
   


#log-out

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')





if __name__=='__main__':
    app.run(debug=True)

