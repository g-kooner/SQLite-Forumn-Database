import sys
import sqlite3
from datetime import datetime

class Votes:
      #create a static var for pid
      #access through an instance or direct thru the class 
      vno = 0

postId = 0

###################################################
#CONNECT TO DATABASE AND SETUP CURSOR OBJECT
def connect(path):
  global connection, cursor
  connection = sqlite3.connect(path)
  #connection = sqlite3.connect(sys.argv[1])
  cursor = connection.cursor()
  cursor.execute(' PRAGMA forteign_keys=ON; ')
  connection.commit()
  return

####################################################
#INTIAL SIGN UP / LOGIN
def firstScreen():
	print("1)Login\n2)Signup")
	option = int(input("Select an option: "))
	if option == 1:
		login()
	elif option == 2:
		signup()
######################################################
#SIGN UP AND LOGIN
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
	print("Successful signup!")
	

	
	cursor.execute('''INSERT INTO users (uid, name, pwd, city, crdate) VALUES (?,?,?,?,?)''', (userId, name, password, city, currentDate))
	
	connection.commit()
	
	mainMenu(userId)


def login():
	global connection, cursor
	

	validLogin = False
	while validLogin == False: 
		uid = input("Please enter your user id: ")
		pwd = input("Please enter you password: ")
		
		cursor.execute("SELECT * FROM users where uid = :uid and pwd= :pwd",{'uid':uid, 'pwd':pwd})
		user = cursor.fetchall()
		
		if user:
			print("Successful login!")
			validLogin = True
		else:
			print("User id does not exist. Try again.")


	mainMenu(uid)
################################################################
#MAIN MENU (AFTER LOGIN SCREEN)
def mainMenu(userId):
  global connection, cursor

  flag = True
  while (flag): 
    #menu options for regular / priveleged users
    print("1) Post a question")
    print("2) Search for posts")
    print("3) Post action-Answer")
    print("4) Post action-Vote")
    
    #check if priveleged user
    cursor.execute("SELECT uid FROM privileged ")
    privilegedUsers = cursor.fetchall()
    isPriv = False
    for pUser in privilegedUsers:
      if userId == pUser[0]:
        isPriv = True 

    #priveleged user menu extra features
    if isPriv:
      print("5) Post action-Mark")
      print("6) Post action-Give")
      print("7) Post action-Add")
      print("8) Post action-edit")

    #logout option
    print("i) Logout")
    #exit
    print("ii) Exit")
    print("\n")

    #users option
    checkOption = True
    while checkOption:
      option = input("Select an option: ")
      #check for logout/exit
      if option == 'i' or option == 'ii':
        checkOption = False
      #check if option is valid integer
      try:
        int_option = int(option)
      except ValueError:
        print("Enter valid post id value")
        continue 
      #regular user option check
      if isPriv == False:
        if int_option <= 4 and int_option >=1:
          checkOption = False
      #priveleged user option
      elif int_option <= 9 and int_option >=1:
        checkOption = False
    
    #i-->go to first screen
    if option == 'i':
      #back to login/signup screen
      firstScreen()
    #ii-->exit
    elif option == 'ii':
      exit()
    #1-->post question func call
    elif int(option) == 1:
      postQuestion(userId)
    #2-->Search for Post func call  
    elif int(option) == 2:
      pass
      #searchPost()
    #3-->Post Answer func call
    elif int(option) == 3:
      postAnswer(userId)
    #4-->Vote a Post func call
    elif int(option) == 4:
      votePost(userId)

############################################################
#Post Question
def postQuestion(userId):
  global connection, cursor
  global postId

  currentDate = datetime.today().strftime('%Y-%m-%d')
  
  #take input from users
  qtitle = input("Enter title of question: ")
  qbody = input("Enter body of question: ")

  #access posts class and static var pid
  #print("PostId: ", postId)
  postId = postId + 1
  print("postId updated: ", postId)

  #update posts table
  cursor.execute('''INSERT INTO posts (pid, pdate, title, body, poster) VALUES(?,?,?,?,?);''',(postId,currentDate,qtitle,qbody,userId))

  #update the questions table 
  cursor.execute('''INSERT INTO questions (pid, theaid)VALUES(?,?);''',(postId,None))

  #update the tags table 
  cursor.execute('''INSERT INTO tags (pid, tag)VALUES(?,?);''',(postId,None))

  #commit changes
  connection.commit()
  return

#####################################################################################
#Post Answer
def postAnswer(userId):
  global connection, cursor
  global postId

  currentDate = datetime.today().strftime('%Y-%m-%d')
  postIsQuestion = False

  while postIsQuestion != True:
    #user input which question post to answer
    print("select a post that is a question to answer")
    postToAnswer = input("ID of post to answer: ")
    
    try:
      int_postToAnswer = int(postToAnswer)
    except ValueError:
      print("Enter valid post id value") 
    else:
      #get all question posts --> list of nested tupels
      cursor.execute("SELECT pid FROM questions")
      qposts = cursor.fetchall() 
      for qpost in qposts:
        print("qpost: ", qpost)
        if qpost[0] == None:
          break
        elif int_postToAnswer == int(qpost[0]):
              postIsQuestion = True

  #take answer title and body from users
  atitle = input("Enter title of answer: ")
  abody = input("Enter body of answer: ")

  #increment pid
  #print("before increment postId: ", postId)
  postId = postId + 1
  print("after increment postId: ", postId)

  #update posts table
  cursor.execute('''INSERT INTO posts (pid, pdate, title, body, poster) VALUES(?,?,?,?,?);''',(postId,currentDate,atitle,abody,userId))

  #update the answers table 
  cursor.execute('''INSERT INTO answers (pid, qid)VALUES(?,?);''',(postId,int_postToAnswer))

  #update the questions table 
  #cursor.execute('''UPDATE questions SET theaid = postID ;''',(postId, ))

  #update the tags table 
  cursor.execute('''INSERT INTO tags (pid, tag)VALUES(?,?);''',(postId,None))

  #commit changes
  connection.commit()
  return

############################################################
def votePost(userId):
  global connection, cursor
  global postId

  currentDate = datetime.today().strftime('%Y-%m-%d')
  postIsValid = False
  
  #choose post to vote on
  while postIsValid != True:
    #user input which post to vote
    print("select a post to vote on")
    postToVote = input("ID of post to vote on: ")
    
    try:
      int_postToVote = int(postToVote)
    except ValueError:
      print("Enter valid post id value") 
    else:
      #get all question posts --> list of nested tupels
      cursor.execute("SELECT pid FROM posts")
      posts = cursor.fetchall() 
      for post in posts:
        #print("post: ", post)
        if post[0] == None:
          break
        elif int_postToVote == int(post[0]):
              postIsValid = True

  #compare userID to query the votes table for matching pid and uid
  cursor.execute("SELECT pid,uid FROM votes")
  voteInfo = cursor.fetchall()
  print("voteInfo: ", voteInfo)
  for vote in voteInfo:
    #print("vote: ", vote)
    #empty or initial votes 
    if vote == None:
      postIsValid = True
      break
    #check if user alrdy voted on this post
    elif (int_postToVote == int(vote[0])) and (userId == vote[1]):
      print("user: ",userId, " has already voted on post ", int_postToVote)
      votePost(userId)  

  #query the votes table to get vno for specific post
  cursor.execute("SELECT vno FROM votes V,posts P, users U WHERE P.pid = ? AND U.uid = ? AND P.pid = V.pid ", (int_postToVote, userId))
  currentVno = cursor.fetchall()
  
  #cursor.execute("SELECT V.pid FROM votes V,posts P, users U WHERE U.uid = ? and V.uid = ? ", (userId, userId))
  #postsWithVotes = cursor.fetchall()

  #print("posts with votes by current user: ", postsWithVotes)
  print("currentVno: ", currentVno)
  if currentVno == []:
    updatedVno = 1
  else:
    print("current vote #: ", currentVno)
    #for vno in currentVno:
    updatedVno = currentVno[0][0] + 1
  
  print("updatedVno: ", updatedVno , "for the post: ", int_postToVote)
  
  #update votes table and increment vote  
  cursor.execute('''INSERT INTO votes (pid, vno, vdate, uid) VALUES(?,?,?,?);''',(int_postToVote, updatedVno, currentDate, userId))
  #commit changes
  connection.commit()
  return
   



############################################################
#main
def main():
    global connection, cursor
    
    path="./project1.db"
    #instance of class posts --> static var pid
    #postInstance = Posts() 

    connect(path)
    firstScreen()
    connection.commit()
    connection.close()
    return


main()