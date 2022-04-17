import os
import subprocess

# 遍历目录并获取所有 ql 文件，返回 list
def get_ql_file_path(security_path):
    ql_file_list = []
    
    for item in os.scandir(security_path):
        if item.is_file() and item.name.endswith('.ql'):
            ql_file_list.append(item.path)
        if item.is_dir():
            ql_file_list += get_ql_file_path(item.path)
            
    return ql_file_list
            
ql = get_ql_file_path('./Security')

# 执行 codeql-cli
def run_codeql(database_dir_path, ql_path):
    security = ql_path.split('/')[-1].split('.')[0]
    
    cmd = ['codeql', 'query', 'run', '-d', 
           database_dir_path, 
           ql_path]
    
    rsp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = rsp.communicate()
    security_list = out.decode('utf-8').split('|')
    
    file_list = []
    for item in security_list:
        if item.strip().startswith('file://'):
            file_list.append(item)
            
    return security, file_list

# print(len(ql))

for ql_path in ql:
    print("正在使用: %s" % ql_path)
    print(run_codeql('./Vuln/micro/', ql_path))