今天继续学习 CodeQL，看了楼兰师傅的[《CodeQL与XRay联动实现黑白盒双重校验》](https://www.yuque.com/loulan-b47wt/rc30f7/bd1frn)有所启发，既然可以使用 Python 调用 codeql-cli 进行查询，那么肯定可以批量进行扫描。CodeQL 官方提供了大量安全 QL 查询，如果直接使用这些基础的 QL 进行批量查询，将结果导入到数据库中再由安全人员进行手动分析，是不是会提高审计的效率？

我使用的是官方 Java 库中的 Security 库

```bash
❯ tree .
.
└── CWE
    ├── CWE-020
    │   ├── ExternalAPISinkExample.java
    │   ├── ExternalAPITaintStepExample.java
    │   ├── ExternalAPIsUsedWithUntrustedData.qhelp
    │   ├── ExternalAPIsUsedWithUntrustedData.ql
    │   ├── UntrustedDataToExternalAPI.qhelp
    │   └── UntrustedDataToExternalAPI.ql
    ├── CWE-022
...
```

首先需要遍历目录下所有的 ql 文件，并且将他们的路径保存到一个列表中：

```python
def get_ql_file_path(security_path):
    ql_file_list = []
    
    for item in os.scandir(security_path):
        if item.is_file() and item.name.endswith('.ql'):
            ql_file_list.append(item.path)
        if item.is_dir():
            ql_file_list += get_ql_file_path(item.path)
            
    return ql_file_list
```

如此一来我们便获得了所有的 ql 文件，接着再调用他们，这里有个坑点：qlpack.yml 文件必须放在 py 脚本同级目录

```python
def run_codeql(database_dir_path, ql_path):
    security = ql_path.split('/')[-1].split('.')[0]
    
    cmd = ['codeql', 'query', 'run', '-d', 
           database_dir_path, 
           ql_path]
    
    rsp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = rsp.communicate()
    security_list = out.decode('utf-8').split('|')
    return security, security_list
```

运行结果：

![截屏2022-04-17 13.12.15](https://cdn.bingbingzi.cn/blog/20220417131232.png "运行结果")

很明显这样的数据是没法直接使用的，这里需要对 ql 文件进行一个简单的修改，我使用的是 getLocation() 获取代码路径，结果：

![image-20220417140314957](https://cdn.bingbingzi.cn/blog/20220417140315.png "整理后的结果")

修改后的 Security 我将会放置在 Github 上：https://github.com/binganao/py-auto-codeql，注：此 Security 为官方魔改后的 ql 文件

最终代码：

```python
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
```

## 未来

打算将这个脚本继续开发，查询后的结果进行入库，并加入 WEB 前端使其更直观也更易于使用

## 感谢

[楼兰 - 《CodeQL 学习笔记》](https://www.yuque.com/loulan-b47wt/rc30f7)

[Github - CodeQL](https://github.com/github/codeql)

[l4yn3 - micro_service_seclab](https://github.com/l4yn3/micro_service_seclab/)
