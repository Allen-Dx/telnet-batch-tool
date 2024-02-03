import telnetlib
import os

import time
import threading

print('''
___________    .__                 __    ___________           .__                                                            
\__    ___/___ |  |   ____   _____/  |_  \__    ___/___   ____ |  |                                                           
  |    |_/ __ \|  |  /    \_/ __ \   __\   |    | /  _ \ /  _ \|  |                                                           
  |    |\  ___/|  |_|   |  \  ___/|  |     |    |(  <_> |  <_> )  |__                                                         
  |____| \___  >____/___|  /\___  >__|     |____| \____/ \____/|____/                                                         
             \/          \/     \/                                                                                           
''')
print('注意：“command.txt”文件末行后应手动增加换行符\\n,或使用回车添加一行\n')

os.chdir(os.path.dirname(__file__))
# 打开文件 host
with open('host.txt', 'r') as file:
    ips = file.readlines()
    # 移除每行末尾的换行符
    ips = [line.strip() for line in ips]

    print('读取ip文件成功\n', ips)
with open('information.txt') as information:
    inf = information.read()
    inf = eval(inf)
    password = inf['password']
    username = inf['username']
    port = inf['port']
    maxsize = inf['maxsize']
    waittime = int(inf['waittime'])
    print('\n获取信息成功', '\n密码:' + password, '\n用户名:' + username, '\n端口:' + port, '\n最大线程数：' + maxsize)

# 定义一个信号量，限制线程数量为maxsize
semaphore = threading.Semaphore(int(maxsize))


# 定义执行功能
def execute_command(ip, port):
    semaphore.acquire()

    try:
        tn = telnetlib.Telnet(ip, port)
        tn.read_until(b"Username:")
        tn.write(username.encode('ascii') + b"\n")

        tn.read_until(b"Password:")
        tn.write(password.encode('ascii') + b"\n")
        time.sleep(1)

    except TimeoutError:
        print(ip, '错误！连接失败：超时，进行下一台服务器')
    except:
        print(ip, '错误！进行下一台服务器')
    else:
        print('登录', ip, '成功！')
        for a in range(len(command_list)):

            # 运行命令
            commandstr = command_list[a]
            tn.write(commandstr.encode('ascii'))
            time.sleep(waittime)
            # 等待服务器响应
            response1 = tn.read_very_eager()

            # 将输出保存到文件
            with open('host[' + ip + ']' + '.txt', 'a') as output_file:
                output_file.write(response1.decode('ascii', 'ignore'))

            # 关闭Telnet连接
        tn.write(b"exit\n")
        print('\n\n服务器', ip, '已完成\n\n')
    finally:
        semaphore.release()


# 获取当前时间
time1: str = time.strftime('%Y%m%d_%H%M%S', time.localtime())
print('将删除以往所有输出，是否继续(Yes/No)')
YN = input('请输入：')
if YN == "Yes" or YN == 'y' or YN == 'Y' or YN == 'yes':
    with open('command.txt') as command:
        command_list = command.readlines()
        print('获取命令成功', command_list)
    # 判断是否存在文件夹
    if not os.path.exists('out'):
        # 无则创建
        os.mkdir("out")
    # 切换至out目录,并以当前时间创建文件夹

    os.chdir("out")
    os.mkdir(time1)
    os.chdir(time1)
    for i in range(len(ips)):
        open('host[' + ips[i] + ']' + '.txt', 'w')

# 创建线程池
threads = []

for i in range(len(ips)):
    thread = threading.Thread(target=execute_command, args=(ips[i], int(port)))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
input("所有数据获取均已完成！数据详情查看out文件夹中的"+time1+'文件夹')
