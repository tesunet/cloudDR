"""
paramiko, pywinrm实现windows/linux脚本调用
"""
import paramiko
import winrm
import json


class ServerByPara(object):
    def __init__(self, cmd, host, user, password, system_choice):
        self.cmd = cmd
        self.client = paramiko.SSHClient()
        self.host = host
        self.user = user
        self.pwd = password
        self.system_choice = system_choice

    def exec_linux_cmd(self):
        data_init = ''
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host, username=self.user, password=self.pwd)
        stdin, stdout, stderr = self.client.exec_command(self.cmd, get_pty=True)
        if stderr.readlines():
            exec_tag = 1
            for data in stdout.readlines():
                data_init += data
        else:
            exec_tag = 0
            for data in stdout.readlines():
                data_init += data
        return {
            "exec_tag": exec_tag,
            "data": data_init,
        }

    def exec_win_cmd(self):
        data_init = ""
        s = winrm.Session(self.host, auth=(self.user, self.pwd))
        ret = s.run_cmd(self.cmd)
        if ret.std_err.decode():
            exec_tag = 1
            for data in ret.std_err.decode().split("\r\n"):
                data_init += data
        else:
            exec_tag = 0
            for data in ret.std_out.decode().split("\r\n"):
                data_init += data
        return {
            "exec_tag": exec_tag,
            "data": data_init,
        }

    def run(self):
        if self.system_choice == "Linux":
            result = self.exec_linux_cmd()
        else:
            result = self.exec_win_cmd()
        print(result)
        print(result["data"])
        return result

# if __name__ == '__main__':
# server_obj = ServerByPara(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
# server_obj = ServerByPara(r"C:\Users\a\Desktop\test.bat", "192.168.12.149", "a",
#                           "zxcvbn123", "Windows")
# server_obj = ServerByPara(r"/root/Desktop/test.sh >> log.txt", "192.168.109.132", "root",
#                           "123456", "Linux")
# server_obj.run()
