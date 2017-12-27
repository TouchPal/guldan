# Guldan Web API
> `v1.0.5 2017-12-12 changed_by livexmm.xu`
>  -  修改stats返回

> `v1.0.4 2017-12-11 changed_by livexmm.xu`
>  -  修正获取版本接口

> `v1.0.3 2017-12-09 changed_by alex.zheng`
>  -  增加获取版本
>  -  修改获取组织信息返回, 增加`access_mode`字段
>  -  修改获取项目信息返回, 增加`access_mode`字段

> `v1.0.2 2017-12-07 changed_by livexmm.xu`  
>  -  增加修改组织  
>  -  增加修改项目  
>  -  删除修改配置请求中的ID

> `v1.0.1 2017-12-07 changed_by livexmm.xu`  
>  -  增加注册API  
>  -  去除HTTP头中的`X-Guldan-Token`

> `v1.0.0 2017-12-05 created_by livexmm.xu`


## 登陆登出注册

### `/api/register`
* 用户注册
* Method: `POST`
* Body:

        {
            "name": "your user name",
            "password": "your password"
        }

* Response:

        {  
            "code": 0,  
            "msg": "OK" 
        }  

    OR  
  
        {
            "code": -1,
            "msg": "error message"
        }

### `/api/login`
* 用户登录
* Method: `POST`
* Body:

        {
            "name": "your user name",
            "password": "your password"
        }

* Response:

        {  
            "code": 0,  
            "msg": "OK",
            "data": {
                "session_id": "your login session",  
                "id": "your user id", 
                "name": "your user name"
                "hash": "your user hash",  
            }  
        }  

    OR  
  
        {
            "code": -1,
            "msg": "error message"
        }

* 说明

    在登陆之后，系统会返回这次登录的`session id`，和你的`user hash`，后面的操作都需要在`http header`加入这两个信息进行操作

### `/api/islogin`
* 判断用户是否已经登录
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        empty body

* Response

        {  
            "code": 0,  
            "msg": "OK",
            "data": {
                "session_id": "your login session",
                "id": "your user id",  
                "name": "your user name"
                "hash": "your user hash",  
            }  
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }
        
    OR
        {
            "code": -2,
            "msg": "用户没有登录"
        }

### `/api/logout`
* 用户登出
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        empty body

* Response

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

## User

### `/api/user/<user_id>`
* 修改用户，现在只支持修改密码
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login
        
* Body:

        {
            "new_password": "new password for user"
        }
        
* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

## Organization
### `/api/org`
* 创建组织
* Method: `PUT`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        {
            "name": "your_new_org_name",
            "private": true|false
        }


* Response:

        {
            "code": 0,
            "msg": "OK",
            "data": {
                "id": "the_org_id_for_your_newly_created_org",
                "name": "your org name",
                "visibility": "private|public"
            }
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/org/<org_id>`
* 修改组织
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        {
            "private": true|false
        }


* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/org/<org_id>`
* 删除组织
* Method: `DELETE`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/org/<org_id>`
* 获得组织详细信息
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK",
            "data": {
                "id": "the_org_id",
                "name": "the org name",
                "visibility": "public|private",
                "access_mode": "modifier",
                "privileges": [
                    {
                        "id": "privilege_id",
                        "type": "modifier|viewer|puller",
                        "user_id": "user id who has this privilege on this org"
                        "user_name": "this user's name"
                    },
                    {...},
                    {...}
                ],
                "projects": [
                    {
                        "id": "project_id",
                        "name": "project full name",
                        "parent_id": parent id ,
                        "visibility": "private|public"
                    },
                    {...},
                    {...}
                ]
            }
        }


	OR

        {
            "code": -1,
            "msg": "error message"
        }

    - `privileges`，哪些用户在该组织上有权限，具体是什么权限
    - `projects`，该组织下的项目列表
    - `access_mode`，表示你对访问该组织的访问级别，`modifier`最高可以修改删除项目，`viewer`只能添加项目，`other`只能浏览

### `/api/org`
* 获取该用户可见的所有org信息
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the session id after you login

* response:

        {
            "code": 0,
            "msg": "OK",
            "data": [
                {
                    "id": org_id,
                    "name": "org_name"
                },
                {
                    "id": org_id,
                    "name": "org_name"
                }
            ]
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/org/<org_id>/authorize`
* 组织授权
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        {
            "type": "the privilege type: modifier|viewer|puller",
            "user_id": "the target user id"
        }

* response:

        {
            "code": 0,
            "msg": "OK"
        }
    
    OR

        {
            "code": -1,
            "msg": "error message"
        }


### `/api/org/<org_id>/authorize/<user_id>`
* 删除某个用户的组织授权，不能删除自己的授权
* Method: `DELETE`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

## Project
### `/api/project`
* 创建项目
* Method: `PUT`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        {
            "parent_id": "org under which we are going to create project",
            "name": "your name project name",
            "private": true|false
        }

* Response:

        {
            "code": 0,
            "msg": "OK",
            "data": {
                "id": "the project id for the new created project",
                "name": "project full name",
                "parent_id": "its_org_id",
                "visibility": "private|public"
            }
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/project/<project_id>`
* 修改项目
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        {
            "private": true|false
        }

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }
    
### `/api/project/<project_id>`
* 获取项目的详细信息
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:


        {
            "code": 0,
            "msg": "OK",
            "data": {
                "id": "project_id",
                "name": "project_name",
                "parent_id": "parent_id, this is its org_id",
                "visibility": "private|public",
                "access_mode": "modifier",
                "items": [
                    {
                        "id": "id for this item",
                        "name": "the full name of this item. format is org_name.project_name.item_name"
                    },
                    {...},
                    {...}
                ],
                "privileges": [
                    {
                        "id": "id for this privilege",
                        "type": "the type name for this privilege",
                        "user_id": "user_id",
                        "user_name": "user_name"
                    },
                    {...},
                    {...}
                ]
            }
        }

	OR

            {
                "code": -1,
                "msg": "error message"
            }

	- `access_mode`，表示你对访问该组织的访问级别，`modifier`最高可以修改删除项目，`viewer`只能添加项目，`other`只能浏览

### `/api/project/<project_id>`
* 删除某个项目
* Method: `DELETE`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/project/<project_id>/authorize`
* 为项目授权
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body

        {
            "type": "the privilege type: modifier|viewer|puller",
            "user_id": "the target user id"
        }

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/project/<project_id>/authorize/<target_user_id>`
* 删除某个用户的项目授权，不能删除自己的授权
* Method: `DELETE`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

## Item
> `grey=true`表示灰度版本，不写或者`grey=false`表示正式版本  

### `/api/item?grey=true|false`
* 创建配置项
* Method: `PUT`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        {
            "code": 0,
            "msg": "OK",
            "data": {
                "parent_id": "project_id for this item",
                "name": "item name",
                "content": "content for this item",
                "type": "Plain",
                "private": true|false
            }
        }

* Response:

        {
            "code": 0,
            "msg": "OK",
            "data": {
                "parent_id": "project id",
                "id": "item id",
                "name": "item name",
                "content": "content for this item",
                "type": "Plain",
                "visibility": "private|public"
            }
        }

    OR

        {
            "code": 0,
            "msg": "error message"
        }

### `/api/item/<item_id>?grey=true|false`
* 获得一个配置项详细信息
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response

        {
            "code": 0,
            "msg": "OK",
            "data": {
                "id": "item id",
                "name": "item_full_name",
                "content": "item data",
                "parent_id": "project id",
                "type": "Plain",
                "visibility": "private|public",
                "access_mode": "modifier|viewer",
                "privileges": [
                    {
                        "id": "id for this privilege",
                        "type": "privilege name for this privilege",
                        "user_id": "user id",
                        "user_name": "user name"
                    },
                    {...},
                    {...}
                ]
            }
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/item/<item_id>?grey=true|false`
* 修改一个配置项
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        {
            "content": "the content that you are going to modify",
            "type": "Plain",
            "private": false|true
        }

* Response

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/item/<item_id>?grey=true|false`
* 删除一个配置项
* Method: `DELETE`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }


### `/api/item/<item_id>/authorize?grey=true|false`
* 为配置项授权，灰度版本不支持授权操作，对灰度版本做授权操作会抛出异常
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body

        {
            "type": "the privilege type: modifier|viewer|puller",
            "user_id": "the target user id"
        }

* response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/item/<item_id>/authorize/<target_user_id>?grey=true|false`
* 删除某个用户的配置项授权，不能删除自己的授权
* Method: `DELETE`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/item/<item_id>/upgrade?grey=true|false`
* 全量发布灰度版本
* Method: `POST`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Body:

        empty body

* Response:

        {
            "code": 0,
            "msg": "OK"
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/item/<item_id>/stats`
* 获取配置项的拉取状态信息
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response：

        {
            "code": 0,
            "msg": "OK",
            "data": {
                "name": "item name",
                "stats": [
                    {
                        "ip": "a.b.c.d",
                        "cid": "1234",
                        "ctype": "proxy|client|...",
                        "cver": "lang/0.1.0",
                        "iver": "12",
                        "lver": "11",
                        "pull_time": UNIX_TIMESTAMP,
					    "grey": true|false
                    },
                    {...},
                    {...}
                ]
            }
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }


### `/api/puller/<org_name>/<project_name>/<item_name>`
* 拉取配置项配置
* Method: `GET`
* Header:  

        X-Guldan-Token: user_token_if_public_not_need

* Response:
    * Header:

            X-Guldan-Version: version

    * Body:  
    
        具体的配置项内容

## Version

### `/api/item/<item_id>/versions?limit=xx&offset=xx&order=desc|asc`
* 获取item的版本记录
* Method: `GET`
* Header:

    	X-Guldan-Session-Id: the_session_id_after_you_login
    
* Response：

    	{
    	    "code": 0,
    	    "msg": "OK",
    	    "data": {
        	    "total": how_many_versions_for_this_resource,
        	    "versions": [
            	    {
                	    "id": "version id",
                	    "item_id": "item id",
                	    "content": "current version content",
                	    "type": "the format type of this item version", 
                        "updated_time": "time format like 2017-12-14 14:26:01", 
                	    "visibility": "private|public"
            	    }
        	    ]
        	}
    	}
    
    
    OR

        {
            "code": -1,
            "msg": "error message"
        }
    	
### `/api/item/<item_id>/versions/rollback?version_id=xxx`
* 回滚到对应的配置项版本
* Method: `POST`
* Header:

    	X-Guldan-Session-Id: the_session_id_after_you_login
    	
* Response:

        {
            "code": 0,
            "msg": "OK",
            "data": {
                "id": "item id",
                "name": "item name",
                "type": "item type, string, PLAIN, JSON, XML, YAML",
                "visibility": "private|public",
                "content": "item data"
            }
        }


    OK

        {
            "code": -1,
            "msg": "error message"
        }

## Search
### `/api/users?q=<user_name>`
* 根据用户名搜索用户信息
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK",
            "data": [
                {"id": "user id", "name": "user name"},
                {...},
                {...}
            ]
        }

    OR

        {
            "code": -1,
            "msg": "error message"
        }

### `/api/resource/search?q=<resource name>`
* 搜索资源
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the_session_id_after_you_login

* Response:

        {
            "code": 0,
            "msg": "OK",
            "data": [
                {
                    "id": "resource id",
                    "name": "resource name",
                    "visibility": "private|public"
                }
            ]
        }

### `/api/audit/search?q=<resource name>&limit=<limit>&offset=<offset>`
* 搜索操作历史
* Method: `GET`
* Header:

        X-Guldan-Session-Id: the session id after you login

* Response:

        {
            "code": 0,
            "msg": "OK",
            "data": {
                total: how_many_audits_for_this_resource,
                audits: [
                    {
                        "content": {
                            "before": "...",
                            "after": "..."
                        },
                        "op_name": "modify",
                        "op_time": "2017-12-05 20:37:36",
                        "resource_id": "1",
                        "resource_type":"item",
                        "resource_visibility":{
                           "after": "private",
                           "before": "public"
                        },
                        "type": {
                           "before": "...",
                           "after": "...
                        },
                        "user_id": "1",
                        "user_name": "user name"
                    },
                    {...},
                    {...}
                ]
            }
        }


    OR

        {
            "code": -1,
            "msg": "error message"
        }



