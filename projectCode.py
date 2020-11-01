import sys
import sqlite3
from datetime import datetime
from collections import defaultdict

class Votes:
      #create a static var for pid
      #access through an instance or direct thru the class 
      vno = 0

#global variable 
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
  flag = True
  while flag:
    print("1)Login\n2)Signup")
    try:
      option = int(input("Select an option: "))
    except ValueError:
      print("Pick a valid option")
    else:
      if option == 1:
        login()
      elif option == 2:
        signup()
      else:
        print("Pick a valid option")
    
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
      if int_option <= 2 and int_option >=1:
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
      searchPosts(userId)
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
  #query the posts table for pid selected by user and specific userId
  cursor.execute("SELECT P.pid FROM posts P")
  postId = cursor.fetchall()

  print("before increment postId: ", postId)
  #intia;/first post made
  if postId == []:
    postId = 1
  else:
    #assign pid based on how many posts in db
    postId = len(postId) + 1

  print("after increment postId: ", postId)

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
#Search Posts
def searchPosts(userId):
  global connection, cursor
  keywords = input("Enter keywords (seperate by space): ")
  keywords = keywords.split()
  posts = {}
  #dict with values as list storage
  tagsDict = defaultdict(list)

  #post info ifnull(tag, '')
  cursor.execute("SELECT p.pid,pdate,title,body,poster,ifnull(numVotes,0),ifnull(numAns,0)\
                  FROM posts p LEFT OUTER JOIN  tags t ON t.pid = p.pid and t.tag IS NOT NULL\
                               LEFT OUTER JOIN (SELECT pid AS vpid, max(vno) AS numVotes FROM votes v GROUP BY pid) ON p.pid = vpid\
                               LEFT OUTER JOIN (SELECT a.qid AS qid, count(*) AS numAns FROM answers a GROUP BY qid) on p.pid = qid")
  #list of posts with info
  resultPosts = cursor.fetchall()
  # for res in resultPosts:
  #   print("res row: ", res )



  #tag words for specific post
  cursor.execute("SELECT t.pid, t.tag FROM tags t, posts p WHERE p.pid = t.pid")
  tags = cursor.fetchall()

  #query for all distinct pids
  cursor.execute("SELECT DISTINCT p.pid FROM posts p")
  distinctPids = cursor.fetchall()


  for tag in tags:
    for pid in distinctPids:
      # print("type of tag0: ", type(tag[0]))
      # print("tag[0] --> pid: ",tag[0])
      # print("tag[1] --> tag: ",tag[1])
      # print("pid: ",pid)
      # print("\n")
      #checks if t.pid matches distinct pids and its tag is not none
      if (tag[0] == pid[0]) and (tag[1] != ''):
        tagsDict[tag[0]].append(tag[1])
  #print("tagsDict: ", tagsDict)

  #combining the tagsDict and resultPosts
  for keyTags in tagsDict.keys():
    for res in resultPosts:
      #comparing pids to check if same
      if (res[0] == keyTags): #and (res[5] != ''):
        #convert res to list 
        resList = list(res)
        #append tags to the res list
        resList.append(tuple(tagsDict[keyTags]))
        #convert back to tuple
        finalRes = tuple(resList)
        #print("final res: ", finalRes)
        posts[finalRes] = 0
  

  #keep track if keyword found
  keywordFound = False
  #counts for keywords
  for res in posts:
    count = 0
    for word in keywords:
      #check if keyword in title or body
      if (word.lower() in res[2].lower()) or (word.lower() in res[3].lower()):
        count = count + 1
      #loop to check the tags --> increment count only if tag not none and count = 0
      for tag in res[7]:
        if (tag != None) and (count == 0):
          if word.lower() in tag.lower():
            count = count + 1
      if count>=1:
        posts[res] = count
        #checks if @ least 1 keyword found
        #keyword found in atleast one post
        keywordFound = True
  
  #keyword not found in all posts then loop back
  if not keywordFound:
    print("\nKEYWORD NOT FOUND\n")
    mainMenu(userId)
  
  # print("\n")
  # print("postDict: ")
  # #print posts dict
  # for keys,values in posts.items():
  #   print("post info / value: ", keys,values)


  # #print the posts dict
  # print("\nposts dict: \n")
  # #print(posts)

  # for keys,values in posts.items():
  #   print("post info: ", keys)
  #   print("values: ",values)
  
  
  
  orderedPosts = sorted(posts.items(), key=lambda x: x[1], reverse=True)
  # for row in orderedPosts:
  #   print("ordered posts: ", row)
  
  #intial setup for post start and post end indices
  postStartIndex = 0
  postEndIndex = 5
  

  flag = True
  while flag == True:
    #format and print the resutls of search for post
    print("{:<8} {:<15} {:<15} {:<20} {:<10} {:<10} {:<10}".format('Post id','Date','Title','Body','Poster','Votes','Answers'))
    for i in orderedPosts[postStartIndex : postEndIndex]:
      body=i[0][3]
      title = i[0][2]
      if len(body)>15:
        body = body[:15]+'...' 
      if len(title)>10:
        title = title[:10]+'...'
      print ("{:<8} {:<15} {:<15} {:<20} {:<10} {:<10} {:<10}".format(i[0][0], i[0][1], title,body,i[0][4], i[0][5], i[0][6]))

    #select post to answer
    # #scrolling
    # #select post to vote
    #menu of what to do with posts

    print("\nWould you like to...  ")
    print("0) Main Menu")
    print("1) See next posts")
    print("2) See previous posts ")
    print("3) Select post to answer")
    print("4) Select post to vote on ")
    #priveleged user menu 
    #check if priveleged user
    cursor.execute("SELECT uid FROM privileged ")
    privilegedUsers = cursor.fetchall()
    isPriv = False
    for pUser in privilegedUsers:
      if userId == pUser[0]:
        isPriv = True 

    #priveleged user menu extra features(only display if priv)
    if isPriv:
      print("5) Post action-Mark")
      print("6) Post action-Give")
      print("7) Post action-Add Tag")
      print("8) Post action-edit")
    
    try:
      option = int(input("Select an option: "))
    except ValueError:
      print("Pick a valid option")
      continue
    else:
      #go back to main menu
      if option == 0:
        mainMenu(userId)

      #see next posts
      #python truncates out of bounds values when slicing
      if option == 1:
        if postEndIndex < len(orderedPosts):
          postStartIndex = postStartIndex + 5
          postEndIndex = postEndIndex + 5
        else:
          print("\nNO MORE POSTS\n")
      
      #see prev posts
      if option == 2:
        if postStartIndex >=5:
          postStartIndex = postStartIndex - 5
          postEndIndex = postEndIndex - 5
        else:
          print("\nNO MORE PREVIOUS POSTS\n") 

      #select a post to answer    
      if option == 3:
        postIsQuestion = False
        while postIsQuestion != True:
          #user input which question post to answer
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
                #selected post is a question --> call postAnswer(userId,pid)
                postAnswer(userId,int_postToAnswer)
        
      #vote on a post
      if option == 4:
        postIsValid = False
        #choose post to vote on
        while postIsValid != True:
          #user input which post to vote
          postToVote = input("ID of post to vote on: ")
          #check if valid int pid
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
                votePost(userId, int_postToVote)
      
      if isPriv:
        #priv user Post Action Mark
        if option == 5 :
          print("test1")
        
        #priv user Post-Action-Give Badge
        if option == 6:
          print("test1")

        #priv user Post-Action-Add Tag
        if option == 7:
          postIsValid = False
          #choose post to vote on
          while postIsValid != True:
            #user input which post to vote
            postToTag = input("ID of post to tag: ")
            #check if valid int pid
            try:
              int_postToTag = int(postToTag)
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
                elif int_postToTag == int(post[0]):
                  postIsValid = True
                  postActionAddTag(userId, int_postToTag)

        #priv user Post-Action-Edit
        if option == 8:
          print("test1")

  return
    
#####################################################################################
#Post Answer
def postAnswer(userId,int_postToAnswer):
  global connection, cursor
  #global postId

  currentDate = datetime.today().strftime('%Y-%m-%d')
  
  #take answer title and body from users
  atitle = input("Enter title of answer: ")
  abody = input("Enter body of answer: ")

  #query the posts table for pid --> gives # of posts total
  cursor.execute("SELECT P.pid FROM posts P")
  postNum = cursor.fetchall()

  print("before increment postNum: ",postNum )
  #intia;/first post made
  if postNum == []:
    postId = 1
  else:
    #increment the pid
    postId = len(postNum) + 1

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
  #call main menu
  mainMenu(userId)

  return

############################################################
def votePost(userId, int_postToVote):
  global connection, cursor
  global postId

  currentDate = datetime.today().strftime('%Y-%m-%d')
  
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
      #check if user has voted on all posts
      #query distinct pids from votes and compare with total posts to check if user has voted on all  posts
      cursor.execute("SELECT DISTINCT V.pid FROM votes V WHERE V.uid = ?", (userId,))
      distinctPids = cursor.fetchall()
      cursor.execute("SELECT P.pid FROM posts P")
      totalPids = cursor.fetchall()
      #sort and compare lists
      distinctPids.sort()
      totalPids.sort()
      
      print("distinct pids: ", distinctPids)
      print("total pids: ", totalPids)

      #call main menu if voted on all posts 
      if distinctPids == totalPids:
        print("user has voted on all possible votes return to main menu")
        mainMenu(userId)
  
      #go back to search post menu
      return  

  #query the votes table to get vno for specific post
  #cursor.execute("SELECT vno FROM votes V,posts P, users U WHERE P.pid = ? AND U.uid = ? AND P.pid = V.pid ", (int_postToVote, userId))
  cursor.execute("SELECT vno FROM votes V WHERE pid = ?", (int_postToVote,))  
  currentVno = cursor.fetchall()
  
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
  #send to main menu
  mainMenu(userId)
  return


############################################################
#TAGS
def postActionAddTag(userId, int_postToTag):
  global connection, cursor
  global postId

  #user picks tag to insert on chosen post
  user_Tag = input("insert tag: ")

  #selected_posts_tags has all tags for the post
  cursor.execute("SELECT T.tag from tags T, posts P WHERE T.pid = P.pid AND P.pid = ?", (int_postToTag,))
  selected_posts_tags = cursor.fetchall()

  print("selected posts tags: ", selected_posts_tags)
  #condition to check if tag already used
  for tag in selected_posts_tags:
    #print("tag: ",tag)
    #print("user tag: ", user_Tag)
    #tag[0] will always be none
    #check if tag is not none
    if(tag[0] == None and len(selected_posts_tags) == 0):
      break
    if (tag[0] != None) and (user_Tag.lower() == tag[0].lower()):
      print("\nTAG IS ALREADY USED\n")
      #addTag(userId)
      mainMenu(userId)
  #update tags table 
  cursor.execute('''INSERT INTO tags (pid, tag) VALUES(?,?);''',(int_postToTag, user_Tag))
  #confirms to user their tag was added
  print("\nTAG ADDED\n")
  #commit changes
  connection.commit()
  mainMenu(userId)


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