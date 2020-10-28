import sqlite3
from datetime import datetime
def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return


def signup():
	global connection, cursor
	currentDate = datetime.today().strftime('%Y-%m-%d')
	

	validUid = False
	while validUid == False:
		userId = input("Enter a user id: ")
		cursor.execute("SELECT * FROM users where uid = ?",(userId,))

		if cursor.fetchall():
			print("User id already taken. Please try again.")
		else:
			validUid = True

		
	name = input("Enter your name: ")
	password = input("Enter a password: ")
	city = input("Enter your city: ")
	

	
	cursor.execute('''INSERT INTO users (uid, name, pwd, city, crdate) VALUES (?,?,?,?,?)''', (userId, name, password, city, currentDate))
	
	connection.commit()
	
	return


def login():
	global connection, cursor
	

	validLogin = False
	while validLogin == False: 
		uid = input("Please enter your user id: ")
		pwd = input("Please enter you password: ")
		
		cursor.execute("SELECT * FROM users where uid = :uid and pwd= :pwd",{'uid':uid, 'pwd':pwd})
		user = cursor.fetchall()
		
		if user:
			print("Successful login")
			validLogin = True
		else:
			print("User id does not exist. Try again.")


	return
def postQuestion(userId):
  global connection, cursor
  global postId 
  currentDate = datetime.today().strftime('%Y-%m-%d')
  
  #take input from users
  qtitle = input("Enter title of question: ")
  qbody = input("Enter body of question: ")

  #assigns pid to post
  if postId == 0:
    postId = 0
  else:
    postId = postId + 1
  postId = str(postId)

  #update posts table
  cursor.execute('''INSERT INTO posts (pid, pdate, title, body, poster) VALUES(?,?,?,?,?);''',(postId,currentDate,qtitle,qbody,userId))

  #update the questions table 
  cursor.execute('''INSERT INTO questions (pid, theaid)VALUES(?,?);''',(postId,None))

  #commit and clost the connections
  connection.commit()
  


def main():
    global connection, cursor
    global postId
    postId=0

    path="./project1.db"
    connect(path)
    #signup()
    #login()
    postQuestion('u200')


    connection.commit()
    connection.close()
    return

if __name__ == "__main__":
	main()
