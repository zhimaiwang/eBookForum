#Written by Zhimai Wang

from socket import *
import threading
import time
import json
import sys


mode = str(sys.argv[1])
polling_interval = float(sys.argv[2])
user_name = str(sys.argv[3])
serverName = str(sys.argv[4])
serverPort = int(sys.argv[5])
#Create a socket, using IPv4 and TCP
clientSocket = socket(AF_INET, SOCK_STREAM)
#clientSocket connect the server using the serverName and serverPost unput
clientSocket.connect((serverName, serverPort))

post_has_read = {}

#The first time to display a book content
def initialize():
    command_pull = raw_input('Plz input:')
    command_pull = command_pull + ' ' + user_name
    clientSocket.send(command_pull)
    command_pull_list = command_pull.split(' ')
    action = command_pull_list[0]
    if action == 'display':
        read_post = list(post_has_read.viewkeys())
        json_read_post = json.dumps(read_post)
        clientSocket.send(json_read_post)
        json_book_content = clientSocket.recv(1024)
        book_content = json.loads(json_book_content)
        for i in book_content:
            if i != 'END':
                print i

def pullmode():
    while True:
        command_pull = raw_input('Plz input:')
        command_pull = command_pull + ' ' + user_name
        clientSocket.send(command_pull)
        command_pull_list = command_pull.split(' ')
        action = command_pull_list[0]
        #Receive content of book from the server and display in the reader window.
        if action == 'display':
            read_post = list(post_has_read.viewkeys())
            json_read_post = json.dumps(read_post)
            clientSocket.send(json_read_post)
            json_book_content = clientSocket.recv(1024)
            book_content = json.loads(json_book_content)

            for i in book_content:
                if i != 'END':
                    print i
        #Send a new post to the server
        if action == 'post_to_forum':
            print 'post has been sent to server'
        #Read psots of the appointed line of the book being read
        #If the reader has never read any posts, it will display all the post of the appointed line;
        #if the reader has read the former posts of the appointed line,
        #it will only display the posts have never been read.
        if action == 'read_post':
            json_post = clientSocket.recv(1024)
            temp_read_post = json.loads(json_post)

            if len(post_has_read) == 0:
                list_id = []
                for i in list(temp_read_post.viewkeys()):
                    list_id.append(eval(i)[3])
                list_id.sort()

                title_list = eval(list(temp_read_post.viewkeys())[0])
                title_list = list(title_list)
                title = 'Book by {}, Page {}, Line number {}:'.format(title_list[0].capitalize(),title_list[1],title_list[2])
                title = title.replace('\'', '')
                print title

                for i in list_id:
                    for j in list(temp_read_post.viewkeys()):
                        if eval(j)[3] == i :
                            print eval(j)[3], '.', temp_read_post[j][0] + ': ' + temp_read_post[j][1]

                for i in list(temp_read_post.viewkeys()):
                    post_has_read[eval(i)] = temp_read_post[i]
            else:
                list_id = []
                new_temp_read_post = {}
                for i in list(temp_read_post.viewkeys()):
                    new_temp_read_post[eval(i)] = temp_read_post[i]
                key_temp_read_post = list(new_temp_read_post.viewkeys())

                for i in key_temp_read_post:
                    if i in list(post_has_read.viewkeys()):
                        key_temp_read_post.remove(i)

                for i in key_temp_read_post:
                    list_id.append(i[3])
                list_id.sort()

                title_list = list(temp_read_post.viewkeys())[0]
                title_list = list(title_list)
                title = 'Book by {}, Page {}, Line number {}:'.format(title_list[0].capitalize(), title_list[1], title_list[2])
                title = title.replace('\'', '')
                print title
                for i in list_id:
                    for j in key_temp_read_post:
                        if j[3] == i:
                            print j[3], '.', new_temp_read_post[j][0] + ': ' + new_temp_read_post[j][1]
                for i in key_temp_read_post:
                    post_has_read[i] = new_temp_read_post[i]
#Automatically check the server whether there are new posts.
#If there are new post, the reader will display 'There are new posts';
#otherwise, it will display 'No new posts'.
def autocheck():
    while True:
        time.sleep(3)
        command_auto = 'auto_check'
        clientSocket.send(command_auto)
        if command_auto == 'auto_check':
            json_pull_list = clientSocket.recv(1024)
            temp_pull_list = json.loads(json_pull_list)
        pull_list = {}
        for i in temp_pull_list:
            pull_list[eval(i)] = temp_pull_list[i]

        key_has_read = list(post_has_read.viewkeys())
        key_pull_list = list(pull_list.viewkeys())
        if len(key_has_read) == 0:
            if len(key_pull_list) == 0:
                print 'No new posts.'
            else:
                print 'There are new posts.'
        else:
            for i in key_has_read:
                key_pull_list.remove(i)
            if len(key_pull_list) == 0:
                print 'No new posts.'
            else:
                print 'There are new posts.'
#Initialize the local database.
#If the the length of the newest post list is larger than that of the local database,
#it will remind the push mode user 'There are new posts'.
def pushmode():
    while True:
        command_initial = 'push_initialize'
        clientSocket.send(command_initial)
        if command_initial == 'push_initialize':
            json_initial_list = clientSocket.recv(1024)
            initial_list = json.loads(json_initial_list)
        #print 'initialized'
        while True:
            command_push = 'push'
            clientSocket.send(command_push)
            if command_push == 'push':
                json_push_list = clientSocket.recv(1024)
                push_list = json.loads(json_push_list)
                if len(initial_list) < len(push_list):
                    print 'There are new posts.'
                    break

#Create three threads
#Reference from:http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb
#493182103fac9270762a000/001386832360548a6491f20c62d427287739fcfa5d5be1f000
t1 = threading.Thread(target=pullmode)
t2 = threading.Thread(target=autocheck)
t3 = threading.Thread(target=pushmode)

if __name__ == '__main__':
    #Pull mode:
    #After initializing, threads t1 and t2 starts simultaneously.
    #Thread t1 gets commands such as 'display', 'post_to_forum' and 'read_post'
    #and send these commands to the server to get corresponding response.
    #Thread t2 keeps sending command 'auto_check' to the server to get the newest post database.
    #If there are posts which have not been read, the reader will display 'There are new posts';
    #otherwise, it will display 'No new posts'.
    if mode == 'pull':
        initialize()
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    #Push mode:
    #After initializing, threads t1 and t3 starts simultaneously.
    #Thread t1 gets commands such as 'display', 'post_to_forum' and 'read_post'
    #and send these commands to the server to get corresponding response.
    #Thread t3 sends 'push_initialize' to initialize the local database.
    #After that, t3 keeps sending 'push' to get the newest post database.
    #If there are new posts for the book being read, the push mode user will receive a message,
    #'There are new posts'.
    elif mode == 'push':
        initialize()
        t1.start()
        t3.start()
        t1.join()
        t3.join()

    clientSocket.close()
