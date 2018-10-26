#Written by Zhimai Wang

from socket import *
from thread import *
import sys
import json

#serverPost is get from the input command.
serverPort = int(sys.argv[1])
#Create a socket, using IPv4 and TCP.
serverSocket = socket(AF_INET, SOCK_STREAM)
#Bind socket with default address and port number entered
serverSocket.bind(('', serverPort))
#Server listening for the connection of clients
serverSocket.listen(10)

pull_list = {}

def clientthread(connection_socket):
    while True:
        command = connection_socket.recv(1024)
        command_list = command.split(' ')
        action = command_list[0]
        #Display command enable server to return the content of the book.
        #If the pull list is empty, the content will not contain 'n' or 'm' symbol.
        #If there are posts in the pull list, the content will be add 'n' or 'm' symbol,
        #which stand for  are new posts' and There are posts, but has been read'.
        if action == 'display':
            book_name = command_list[1]
            page_num = command_list[2]
            book = str(book_name) + '_page' + str(page_num)
            temp_book = []
            json_post_has_read = connection_socket.recv(1024)
            post_has_read = json.loads(json_post_has_read)
            label_content = {}
            new_post = {}
            if len(post_has_read) == 0:
                if len(pull_list) == 0:
                    with open(book, 'r') as files:
                        for line in files:
                            line = line.replace('\n', '')
                            temp_book.append(line)
                    temp_book.append('END')
                    json_book_content = json.dumps(temp_book)
                    connection_socket.send(json_book_content)

                elif len(pull_list) != 0:
                    for i in list(pull_list.viewkeys()):
                        if i[0] == book_name and i[1] == page_num:
                            label_content[i[2]] = 'n'
                    with open(book, 'r') as files:
                        for line in files:
                            if line[3] in list(label_content.viewkeys()):
                                line = line.replace('\n', '')
                                line = line[: 0] + str(label_content[line[3]]) + line[1 :]
                                temp_book.append(line)
                            else:
                                line = line.replace('\n', '')
                                temp_book.append(line)
                    temp_book.append('END')
                    json_book_content = json.dumps(temp_book)
                    connection_socket.send(json_book_content)
            else:
                for i in post_has_read:
                    label_content[i[2]] = 'm'
                key_pull_list = list(pull_list.viewkeys())
                for i in post_has_read:
                    key_pull_list.remove(tuple(i))

                for i in key_pull_list:
                    if i[0] == book_name and i[1] == page_num:
                        label_content[i[2]] = 'n'

                with open(book, 'r') as files:
                    for line in files:
                        if line[3] in list(label_content.viewkeys()):
                            line = line.replace('\n', '')
                            line = line[: 0] + str(label_content[line[3]]) + line[1:]
                            temp_book.append(line)
                        else:
                            line = line.replace('\n', '')
                            temp_book.append(line)
                temp_book.append('END')
                json_book_content = json.dumps(temp_book)
                connection_socket.send(json_book_content)
        #Add post to the destination line
        #The type of pull_list is dictionary whose keys are serial number
        #and values are lists composed of user_name and post_content.
        if action == 'post_to_forum':
            line_num = command_list[1]
            post_content_list = command_list[2 : -1]
            user_name = command_list[-1]
            post_content = ''
            for i in post_content_list:
                post_content += i + ' '
            print post_content

            if len(pull_list) == 0:
                serial_num = (book_name, page_num, line_num, 1)
                pull_list[serial_num] = [user_name, post_content]
            else:
                id_list = []
                for i in list(pull_list.viewkeys()):
                    if i[0] == book_name and i[1] == page_num and i[2] == line_num:
                        id_list.append(i[3])
                if len(id_list) == 0:
                    serial_num = (book_name, page_num, line_num, 1)
                    pull_list[serial_num] = [user_name, post_content]
                else:
                    max_id = max(id_list) + 1
                    serial_num = (book_name, page_num, line_num, max_id)
                    pull_list[serial_num] = [user_name, post_content]
            message = 'New post received from {} \n' \
                      'Post added to the database and given serial number {}.\n' \
                      'Push list empty. No action required.'.format(user_name, serial_num)
            message = message.replace('\'', '')
            print message
        #Return the post of the appointed book, page and line
        if action == 'read_post':
            line_num = command_list[1]
            read_post = {}
            for i in list(pull_list.viewkeys()):
                if i[0] == book_name and i[1] == page_num and i[2] == line_num:
                    read_post[i] = pull_list[i]
            json_read_post = json.dumps({str(k): v for k, v in read_post.items()})
            connection_socket.send(json_read_post)
        #If the user is in pull mode, the reader will automatically check the server
        #whether there are new posts.
        if action == 'auto_check':
            temp_pull_list = {}
            for i in pull_list:
                if i[0] == book_name and i[1] == page_num:
                    temp_pull_list[i] = pull_list[i]
            json_pull_list = json.dumps({str(k): v for k, v in temp_pull_list.items()})
            connection_socket.send(json_pull_list)
        #If the user is in push mode, it will initialize a database of post already in the server.

        if action == 'push_initialize':
            initial_list = {}
            for i in list(pull_list.viewkeys()):
                if i[0] == book_name and i[1] == page_num:
                    initial_list[i] = pull_list[i]
            json_initial_list = json.dumps({str(k): v for k, v in initial_list.items()})
            connection_socket.send(json_initial_list)

        if action == 'push':
            push_list = {}
            for i in list(pull_list.viewkeys()):
                if i[0] == book_name and i[1] == page_num:
                    push_list[i] = pull_list[i]
            json_push_list = json.dumps({str(k): v for k, v in push_list.items()})
            connection_socket.send(json_push_list)

if __name__ == '__main__':
    welcome_message = 'The server is listening on post number {}.\n' \
                      'The database for discussion posts has been initialised.'.format(serverPort)
    print welcome_message

    while True:
        #Accept the socket and address sent from the reader
        connection_socket, addr = serverSocket.accept()
        #Multiple threads enables the server to connect with different readers
        start_new_thread(clientthread, (connection_socket,))

    connection_socket.close()
    serverSocket.close()


