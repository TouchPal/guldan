# guldan简介
guldan是一个配置管理中心，通过guldan用户可用方便的实现自己应用的配置管理。

   * 配置热变更，当配置变更时，guldan会及时的通知到应用，应用感知到变化，并作出自己的相应及调整；比如，流量切换，服务开关等。
   * guldan还允许配置共享，当你想要把自己的配个配置共享给其他业务方时，可以将该配置项授权，让其访问，比如mysql slave库的共享

架构如下图所示

![guldan架构图](./docs/guldan_arch.png)

## guldan中的概念

1. 用户
    * guldan采用单独的用户体系，需要先在guldan中注册才能使用
    * 用户注册后，会被生成一个唯一hash，该hash即用户的token，授权时是以该hash为标准的
    * 用户可以修改自己的密码；当用户忘记密码时，可以联系系统管理员admin进行重置密码
    * 系统在启动的时候，默认会创建一个admin用户，密码123456，在将系统发布给用户使用前，请先修改admin密码

2. 配置
    * 配置分为三个层级，（org， project， item）
    * 每个层级中创建资源的名称都是唯一的，比如在org层，名字不能有重复，在单个org中，各个project名字不能有重复，在单个project中，各个item的名字不能有重复
    * 但是如果是不同的project，是可以有相同的配置项名称的，比如project1和project2都可以有mysql_master这个配置项
    * 配置可以授权给其他人，在授权的时候，通过搜索对方的用户名，找到并授权

3. 用户的权限
    * 当授权给用户时，需要选择相应的权限，已决定该用户将要获得的权限。
    * 现在的权限分为三个
        * modifer
        * viewer
        * puller
    * puller只是具有配置的拉取权限，该用户只能在程序中获得该配置项的内容，他在guldan的web将看不到任何关于该配置项的内容
    * viewer在具有puller的权限的同时，可以在guldan的web界面上看到该配置项的内容，但是不能修改
    * modifier在具有viewer的权限的同时，还可以对该配置项的内容进行修改
    * 一个资源的创建者默认对其创建的资源具有modifier权限

4. 配置的可见性
    * 公开，任何用户都可以看到该资源的内容，但是不能修改
    * 私有，只有授权过的用户才可以对该资源进行拉取，查看或修改
    * viewer默认只能查看某一层次内的公有和授权过的资源，看不到其它未授权的资源
    * viewer可以在某一层次上创建新的资源，该viewer对新创建的资源默认具有modifier权限

# guldan接入指南
## 接入方式

现提供一下两种客户端使用方式

1. 嵌入到应用中（即跟应用在同一个进程中）的guldan client，guldan client有多语言版本
    1. python
    1. c
    1. go
    1. java
1. 处在应用外（即单独的一个进程）的guldan proxy

### python client

具体的使用方式，可以参见[python client](https://github.com/TouchPal/pguldan)

### go client

具体的使用方式，可以参见[go client](https://github.com/TouchPal/guldan-go)

### java client

具体的使用方式，可以参见[java client](https://github.com/TouchPal/jguldan)

### guldan proxy

具体的使用方式，可以参见[guldan proxy](https://github.com/TouchPal/guldan-proxy)

## 配置发布

### 常规发布

正常的配置发布，用户或者客户端直接拉取就可以了。

每一次的配置修改发布都使得配置项的版本号增加，以标识不同的配置项版本。

### 灰度发布

当用户选择灰度发布配置项时，并不会影响主干上的配置项。
用户可以对灰度的配置项做修改和发布操作，但是灰度发布的配置项不支持版本管理。

当用户想要获取配置项的灰度版本时，需要在拉取时，带上grey=true的选项，这样拉取的就是灰度发布的版本了。
如果用户使用我们提供的客户端，该选项会自动带上。

## 说明

由于这两个环境并没有打通，也就是说这两套系统是完全独立的，所以你在测试环境上做过的测试，在上线之前请务必确认在生产环境上也做了配置。

# guldan web api

为了方便通过程序的方式来管理guldan，我们提供了web api

* [guldan web api](./docs/api.md)

# guldan部署

## guldan环境初始化

```bash
    cd guldan_root
    virtualenv guldanenv
    source guldanenv/bin/activate
    pip install -r requirements.txt
```

## guldan依赖

以下为guldan的依赖

1. mysql
1. redis
1. kafka（需要zookeeper的地址）

请在部署前，确认申请并设置好以上资源，并做以下的初始化

1. 数据库的初始化，使用[sql文件](./app/api/models/models.sql)
1. 确认你的mysql server使用了utf8mb4编码
1. 准备好mysql的连接串，连接串示例如下：
    1. mysql://root:root@127.0.0.1:3500/guldandb?charset=utf8mb4
1. kafka申请好topic的名字和consumer group的名字
    1. 如果你的kafka管理员不允许自动创建topic，还请先创建好你的topic
1. 确认好kafka的版本号
1. 选择好guldan生成用户hash所需要的盐，它是一个任意长度的字符串，越随机越好
1. 确认好guldan的日志输出目录，提前创建好
1. 确认好guldan在主机上可以监听的端口


## guldan web 部署

确认好以上信息之后，就可以在[config.py](./config.py)中将配置填入AppConfig中。

1. db_master, mysql master的连接串
1. db_slave， mysql slave的连接串
1. protocol, uwsgi运行的协议，socket或者http，生产上推荐使用socket
1. port，guldan的端口
1. redis_url， redis的连接串
1. metrics_url， 监控地址，这里是influxdb的udp地址，不用可以设置为unset
1. kafka_zk， kafka zookeeper的地址
1. kafka_brokers， kafka的broker地址
1. kafka_item_grey_topic，kafka topic的名字
1. kafka_version， kafka的版本号
1. salt，用户名密码加密所使用到的盐，任意字符串

在确认了以上配置后，将它们放入到环境变量中，

```bash
export db_master=xxx
export db_slave=xxx
....
```

之后再运行

```bash
cd guldan_root
/path/to/your/venv/bin/python guldan_start.py 
```

## guldan async 部署

guldan async是为了接收guldan web发的异步消息来设计的，主要是kafka的消费者

需要的配置如下

1. redis_url， redis连接串
1. metrics_url， 监控地址，这里是influxdb的udp地址，不用可以设置为unset
1. kafka_brokers，kafka的broker地址
1. kafka_zk， kafka zookeeper的地址
1. kafka_item_grey_topic， kafka topic的名字
1. kafka_consumer_group_name， kafka的consumer group的名字
1. kafka_version，kafka的版本号

拿到上面的配置之后，还请把这些配置放入到环境变量中

```bash
export redis_url=xxx
export metrics_url=xxx
....
```

然后执行下面的命令

```bash
cd guldan_root
/path/to/your/venv/bin/python async_consumer/async_consumer.py
```

## guldan docker 部署

### docker 环境准备

1. docker安装

可以参考下面的链接进行docker的安装

https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

1. docker-compose安装

对于ubuntu，可以采用下面的方式安装docker-compose

```bash
sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
1. 确认自己拥有docker命令的执行权限，如果没有，还请联系你的系统管理员，让他把你的用户名加入的docker用户组下。

### guldan docker base 

guldan docker的base镜像，主要是用来安装guldan的依赖的其它的软件包。
因为在开发过程中，guldan的依赖的软件包不会有太大的变化，而且安装依赖软件包也是一个耗时的过程。

base镜像生成使用下面的命令

```bash
    cd guldan_root
    docker build -f dockers/Dockerfile -t guldan_base:latest dockers
```

### guldan web docker

web镜像主要是启动guldan web服务的，使用如下命令生成guldan web镜像，你可以根据自己公司的policy更改生成镜像的tag。

```bash
    cd guldan_root
    docker build -t guldan_web:latest .
```
guldan web的上线，同样需要设置容器的环境变量，配置项同`guldan web部署`中提到的配置

```bash
    docker run -d -e db_master=xxx -e db_slave=xxx -e other configs  guldan_web:latest
```
    
### guldan async docker

跟guldan web docker一样，guldan async docker也是依赖guldan base镜像的

```bash
    cd guldan_root
    docker build -t guldan_async:latest async_consumer
```
    
启动时的环境变量，也请参考上面的`guldan async 部署`

```bash
    docker run -d -e redis_url=xxx -e .... guldan_async:latest 
```


# guldan开发

guldan的整个开发环境也是基于docker的，如果你还没有docker，还请参见上面的`docker 环境准备`.

在项目中提供了`guldan_setup.py`供开发者使用，具体的说明可以见`guldan_setup.py -h`
该命令会以docker的形式启动guldan依赖，以及guldan_web和guldan_async。成功setup之后，他启动了以下6个容器

1. mysql
1. redis
1. zookeeper
1. kafka
1. guldan_web
1. guldan_sync

跟`guldan_setup.py`配合使用的是`guldan_options.yml`文件，该文件中定义了guldan所需要的一些参数，开发者可以根据自己的需要进行修改。

用户需要将其中的`127.0.0.1`替换成自己的开发机器地址，

## 启动guldan

```bash
python guldan_setup.py run --guldan-port=8080 --guldan-option-file="./guldan_options.yml"
```
    
## 删除guldan环境

```bash
python guldan_setup.py down
```

该命令会将启动的docker镜像停止并删除
    
## guldan web reload

如果guldan web的代码有改动，可以使用`reload guldan`； 
由于在开发环境，guldan是以默认的bridge模式启动的，所以下面的启动参数`guldan-port`是主机上guldan映射的端口。

```bash
python guldan_setup.py reload guldan --guldan-port=8080 --guldan-option-file="./guldan_options.yml"
```

## guldan async reload
    
如果guldan async的代码有改动，可以使用`reload guldan_async`

```bash
python guldan_setup.py reload guldan_async --guldan-option-file="./guldan_options.yml"
```

## guldan调试启动
如果你觉得在容器中，对guldan的调试不太方便，还可以使用一下默认启动guldan

1. python方式
    * 因为guldan采用了flask，所以可以是直接使用`python guldan.py`的方式进行启动
    * 由于flask的这种启动方式使用了`werkzeug.serving`包的`run_simple`方法，所以该方式不适合在生产上启动服务，仅用作调试使用
    * 这种启动方式默认使用`config.py`中所定义的一些默认配置项，你需要将guldan的依赖的一些配置放入到这个文件中
1. uwsigi方式
    * 同上，你需要将guldan依赖的配置在`config.py`中填好
    * 使用uwsgi的方式进行启动，`uwsgi guldan_uwsgi_deploy.ini`
    * 因为python的启动方式效率比较低，采用这种方式可以方便前端开发

