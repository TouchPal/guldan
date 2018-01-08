function editor_model(type) {
  if (!!type) {
    const t = type.toUpperCase();
    if (t == "JSON") {
      return "ace/mode/json";
    } else if (t == "XML") {
      return "ace/mode/xml";
    } else if (t == "YAML") {
      return "ace/mode/yaml";
    }
  }
  return "ace/mode/text";
}

function default_error_handle($state, $utils, fn) {
  return function (err) {
    console.log(err);
    $utils.error(err.msg, function() {
      if (err.code == -2) {
        $state.go('dashboard.index');
      } else {
        fn && fn(err);
      }
    });
  }
}

angular.module('guldan.controllers', ['guldan.services'])

.controller('DashboardCtrl', function ($scope, $state, $connection, $utils, $compile) {
  console.log('enter dashboard controller');

  $scope.u = {};
  $connection.islogin().then(function(user) {
    console.log(user);
  	$scope.user = user;
  }).catch(function(err) {
    console.log(err);
  });

  $scope.login = function () {
    if (!$scope.u.name) {
      $utils.error("账号不能为空");
      return;
    } else if (!$scope.u.password) {
      utils.error("密码不能为空");
      return;
    }
    $connection.login($scope.u).then(function(user) {
      $scope.user = user;
      $state.go('dashboard.index');
    }).catch(default_error_handle($state, $utils));
  };
  $scope.login_keyup = function (e) {
    var keycode = window.event ? e.keyCode : e.which;
    if(keycode==13){
      $scope.login();
    }
  };
  $scope.modify_profile = function () {
    $scope.profile_state = {};
    $utils.confirm("<div id='modify-profile'></div>", function(ok) {
      if (ok) {
        console.log($scope.profile_state);
        if (!$scope.profile_state.password) {
          $utils.error("新密码不能为空");
          return;
        }
        if ($scope.profile_state.again_password != $scope.profile_state.password) {
          $utils.error("2次密码输入不一致");
          return;
        }
        $connection.modify_profile($scope.user.id, $scope.profile_state.password).then(function() {
          $utils.success("修改成功");
        }).catch(default_error_handle($state, $utils));
      }
    }, true);
    var msg = "<form class='form-horizontal'>" +
                "<div class='form-group'>" +
                  "<div style='font-size:32px;margin-bottom:10px;padding-left:40px;'>修改个人信息</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<label class='col-sm-2 control-label'>新密码</label>" +
                  "<div class='col-sm-10'>" +
                    "<input type='password' class='form-control' placeholder='新密码' ng-model='profile_state.password' />" +
                  "</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<label class='col-sm-2 control-label'>确认密码</label>" +
                  "<div class='col-sm-10'>" +
                    "<input type='password' class='form-control' placeholder='确认密码' ng-model='profile_state.again_password' />" +
                  "</div>" +
                "</div>" +
              "</form>"
    var compileFn = $compile(msg);
    var $dom = compileFn($scope);
    var $sut = angular.element(document.getElementById('modify-profile'));
    $sut.append($dom);
  };
  $scope.logout = function () {
  	$connection.logout().then(function(result) {
      $scope.user = null;
    }).catch(default_error_handle($state, $utils));
  };
})

.controller('UsersCtrl', function ($scope, $state, $connection, $utils, $compile) {
  console.log('enter users controller');
  $scope.search_users = function() {
    if (!$scope.search_key) {
      $utils.error('搜索用户名不能为空');
      return;
    }
    $connection.search_users($scope.search_key).then(function (users) {
      $scope.users = users;
    }).catch(default_error_handle($state, $utils));
  };
  $scope.modify_user = function(user) {
    $scope.profile_state = {};
    $utils.confirm("<div id='modify-user'></div>", function(ok) {
      if (ok) {
        console.log($scope.profile_state);
        if (!$scope.profile_state.password) {
          $utils.error("新密码不能为空");
          return;
        }
        if ($scope.profile_state.again_password != $scope.profile_state.password) {
          $utils.error("2次密码输入不一致");
          return;
        }
        $connection.modify_profile(user.id, $scope.profile_state.password).then(function() {
          $utils.success("修改成功");
        }).catch(default_error_handle($state, $utils));
      }
    }, true);
    var msg = "<form class='form-horizontal'>" +
                "<div class='form-group'>" +
                  "<div style='font-size:32px;margin-bottom:10px;padding-left:40px;'>修改个人信息</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<label class='col-sm-2 control-label'>新密码</label>" +
                  "<div class='col-sm-10'>" +
                    "<input type='password' class='form-control' placeholder='新密码' ng-model='profile_state.password' />" +
                  "</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<label class='col-sm-2 control-label'>确认密码</label>" +
                  "<div class='col-sm-10'>" +
                    "<input type='password' class='form-control' placeholder='确认密码' ng-model='profile_state.again_password' />" +
                  "</div>" +
                "</div>" +
              "</form>"
    var compileFn = $compile(msg);
    var $dom = compileFn($scope);
    var $sut = angular.element(document.getElementById('modify-user'));
    $sut.append($dom);
  };
})

.controller('RegCtrl', function ($scope, $state, $connection, $utils) {
  console.log('enter reg controller');
  $scope.user = {};
  $scope.submit = function() {
    if (!$scope.user.name || $scope.user.name.length > 32) {
      $utils.error("用户名不符合要求(1-32)个英文字符");
      return;
    }
    if (!$scope.user.password) {
      $utils.error("密码不能为空");
      return;
    }
    if ($scope.user.password != $scope.user.again_password) {
      $utils.error("2次密码输入不一致");
      return;
    }
    $connection.reg({name: $scope.user.name, password: $scope.user.password}).then(function(ok) {
      $utils.success("注册成功", function() {
        $state.go("dashboard.index");
      });
    }).catch(default_error_handle($state, $utils));
  }
})

.controller('ConfigSearchCtrl', function ($scope, $state, $stateParams, $location, $connection, $utils) {
  console.log('enter config search controller');
  var search_key = $stateParams.key || "";
  $scope.page = { search_key: search_key };
  if (!!search_key) {
    console.log("search at begin ", search_key);
    $connection.search_resources(search_key).then(function(resources) {
      $scope.page.resources = resources;
    }).catch(default_error_handle($state, $utils));
  }
  $scope.search_resources = function() {
    $location.search("key", $scope.page.search_key);
    $connection.search_resources($scope.page.search_key).then(function(resources) {
      $scope.page.resources = resources;
    }).catch(default_error_handle($state, $utils, function() {
      $scope.page.resources = [];
      $scope.$apply();
    }));
  }
  $scope.goto_resource = function(resource) {
    const slices = resource.name.split('.');
    if (slices.length == 3) {
      $state.go('dashboard.config.item.index', {iid: resource.id, r: 'search'});
    } else if (slices.length == 2) {
      $state.go('dashboard.config.proj', {prid: resource.id, r: 'search'});
    } else if (slices.length == 1) {
      $state.go('dashboard.config.org', {oid: resource.id, r: 'search'});
    } else {
      $utils.error('资源名错误');
    }
  }
})

.controller('HistoryOperationCtrl', function ($scope, $state, $stateParams, $location, $connection, $utils, $compile) {
  console.log('enter history operation controller');
  var offset = $stateParams.offset || 0;
  var search_key = $stateParams.key || "";
  $scope.page = { offset: offset, search_key: search_key };
  if (!!search_key) {
    console.log("search at begin ", search_key);
    $connection.search_audits($scope.page.search_key, $scope.page.offset).then(function(page) {
      $scope.page = page;
    }).catch(default_error_handle($state, $utils));
  }

  $scope.search_operation_history = function() {
    $location.search("key", $scope.page.search_key);
    $connection.search_audits($scope.page.search_key, $scope.page.offset).then(function(page) {
      $scope.page = page;
    }).catch(default_error_handle($state, $utils, function() {
      $scope.page.audits = [];
      $scope.$apply();
    }));
  }
  $scope.get_prev_history = function() {
    var offset = $scope.page.offset || 0;
    offset = Math.floor(offset / 10) * 10 - 10;
    $connection.search_audits($scope.page.search_key, offset).then(function(page) {
      $location.search("offset", $scope.page.offset);
      $scope.page = page;
    }).catch(default_error_handle($state, $utils, function() {
      $scope.page.audits = [];
      $scope.$apply();
    }));
  }
  $scope.get_next_history = function() {
    var offset = $scope.page.offset || 0;
    offset = Math.floor(offset / 10) * 10 + 10;
    $connection.search_audits($scope.page.search_key, offset).then(function(page) {
      $location.search("offset", $scope.page.offset);
      $scope.page = page;
    }).catch(default_error_handle($state, $utils, function() {
      $scope.page.audits = [];
      $scope.$apply();
    }));
  }

  $scope.show_detail = function (op) {
    $utils.dialog("<div id='flex-container'>" +
                    "<div><div class='acediff-class' id='left-editor'></div></div>" +
                    "<div id='acediff-gutter'></div>" +
                    "<div><div class='acediff-class' id='right-editor'></div></div>" +
                  "</div>", true);
    var differ = new AceDiff({
      left: {
        id: "left-editor",
        mode: editor_model(op.content.before),
        content: op.content.before,
        editable: false,
        copyLinkEnabled: false,
      },
      right: {
        id: "right-editor",
        mode: editor_model(op.content.after),
        content: op.content.after,
        editable: false,
        copyLinkEnabled: false,
      }
    });
  }
})

.controller('ConfigManageCtrl', function ($scope, $compile, $state, $connection, $utils) {
  console.log('enter config manage controller');

  $scope.organizations = [];
  $connection.list_organization().then(function(orgs) {
    console.log(orgs);
    $scope.organizations = orgs || [];
  }).catch(default_error_handle($state, $utils));

  $scope.o = { "name": "", "private": "0" };
  $scope.create_organization = function() {
    $utils.confirm("<div id='create-organization'></div>", function(ok) {
      if (ok) {
        console.log($scope.o);
        if (!$scope.o.name) {
          $utils.error("名字不能为空");
          return;
        }
        let is_private = true;
        if ($scope.o.private == "0") {
          is_private = false;
        }
        $connection.create_organization($scope.o.name, is_private).then(function(o) {
          $scope.organizations.push({"id": o.id, "name": o.name});
        }).catch(default_error_handle($state, $utils));
      }
    }, true);
    var msg = "<form class='form-horizontal'>" +
                "<div class='form-group'>" +
                  "<div style='font-size:32px;margin-bottom:10px;padding-left:40px;'>创建组织</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<label class='col-sm-2 control-label'>组织名称</label>" +
                  "<div class='col-sm-10'>" +
                    "<input type='text' class='form-control' placeholder='最长85个英文字符' ng-model='o.name' />" +
                  "</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<label class='col-sm-2 control-label'>可见性</label>" +
                  "<div class='col-sm-10'>" +
                    "<select class='form-control' ng-model='o.private'>" +
                      "<option value=0>公开</option>" +
                      "<option value=1>私有</option>" +
                    "</select>" +
                  "</div>" +
                "</div>" +
              "</form>"
    var compileFn = $compile(msg);
    var $dom = compileFn($scope);
    var $sut = angular.element(document.getElementById('create-organization'));
    $sut.append($dom);
  }

  $scope.goto_organization = function (organization) {
    console.log("goto: ", organization);
    $state.go('dashboard.config.org', { "oid": organization.id });
  };
})

.controller('OrganizationCtrl', function ($scope, $compile, $state, $stateParams, $connection, $utils) {
  console.log('enter organization controller');
  const oid = $stateParams.oid;

  $connection.get_organization(oid).then(function(o) {
    console.log(o);
    $scope.organization = o;
  }).catch(function(err) {
    console.log(err);
    $utils.error(err.msg, function() {
      if (err.code == -2) {
        $state.go('dashboard.index');
      } else {
        if ($stateParams.r == 'search') {
          $state.go('dashboard.config_search');
        } else {
          $state.go('dashboard.config.index');
        }
      }
    });
  });

  $scope.p = { "name": "", "private": "0" };
  $scope.create_project = function() {
    $utils.confirm("<div id='create-project'></div>", function(ok) {
      if (ok) {
        console.log($scope.p);
        if (!$scope.p.name) {
          $utils.error("名字不能为空");
          return;
        }
        let is_private = true;
        if ($scope.p.private == "0") {
          is_private = false;
        }
        $connection.create_project(oid, $scope.p.name, is_private).then(function(p) {
          $scope.organization.projects.push({"id": p.id, "name": p.name});
        }).catch(default_error_handle($state, $utils));
      }
    }, true);
    var msg = "<form class='form-horizontal'>" +
                "<div class='form-group'>" +
                  "<div style='font-size:32px;margin-bottom:10px;padding-left:40px;'>创建项目</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<label class='col-sm-2 control-label'>项目名称</label>" +
                  "<div class='col-sm-10'>" +
                    "<input type='text' class='form-control' placeholder='最长85个英文字符' ng-model='p.name' />" +
                  "</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<label class='col-sm-2 control-label'>可见性</label>" +
                  "<div class='col-sm-10'>" +
                    "<select class='form-control' ng-model='p.private'>" +
                      "<option value=0>公开</option>" +
                      "<option value=1>私有</option>" +
                    "</select>" +
                  "</div>" +
                "</div>" +
              "</form>"
    var compileFn = $compile(msg);
    var $dom = compileFn($scope);
    var $sut = angular.element(document.getElementById('create-project'));
    $sut.append($dom);
  };
  $scope.update_organization = function() {
    $utils.confirm("是否确认需要修改该组织?", function(ok) {
      if (ok) {
        let is_private = false;
        if ($scope.organization.visibility == "private") {
          is_private = true;
        }
        $connection.update_organization(oid, {"private": is_private}).then(function(ok) {
          $utils.success("已修改成功");
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.delete_organization = function() {
    $utils.confirm("是否确认需要删除该组织?", function(ok) {
      if (ok) {
        $connection.delete_organization(oid).then(function(ok) {
          $utils.success("删除成功", function() {
            $state.go('dashboard.config.index');
          });
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.authorize_organization = function() {
    $utils.dialog("<div id='authorize-organization' style='padding-bottom:20px;'></div>", true);
    $scope.search_key = "";
    $scope.search_users = null;
    $scope.search_users_keyup = function(e) {
      var keycode = window.event ? e.keyCode : e.which;
      if(keycode==13){
        if ($scope.search_key == "") {
          $utils.error("搜索账号不能为空");
          return;
        }
        $connection.search_users($scope.search_key).then(function(users) {
          console.log(users);
          $scope.search_users = users;
        }).catch(default_error_handle($state, $utils));
      }
    };
    $scope.authorize = function(authorize_user) {
      if (authorize_user.role == "delete") {
        $utils.confirm("是否确定回收 " + authorize_user.name + " 的权限", function(ok) {
          if (ok) {
            $connection.cancel_organization(oid, authorize_user.id).then(function(ok) {
              let privileges = $scope.organization.privileges;
              for (let i = 0; i < privileges.length; i++) {
                if (authorize_user.id == privileges[i].user_id) {
                  privileges.splice(i, 1);
                  break;
                }
              }
              $utils.success("取消授权成功");
            }).catch(default_error_handle($state, $utils));
          }
        });
      } else {
        $utils.confirm("是否确定授予 " + authorize_user.name + " 的 " + authorize_user.role + " 权限?", function(ok) {
          if (ok) {
            $connection.authorize_organization(oid, authorize_user.id, authorize_user.role).then(function(ok) {
              for (let i = 0; i < $scope.organization.privileges.length; i++) {
                if ($scope.organization.privileges[i].user_id == authorize_user.id) {
                  $scope.organization.privileges[i].type = authorize_user.role;
                  $utils.success("授权成功");
                  return;
                }
              }
              $scope.organization.privileges.push({
                "id": "0",
                "user_id": authorize_user.id,
                "user_name": authorize_user.name,
                "type": authorize_user.role
              });
              $utils.success("授权成功");
            }).catch(default_error_handle($state, $utils));
          }
        });
      }
    };
    var msg = "<form class='form-horizontal'>" +
                "<div class='form-group'>" +
                  "<div style='font-size:32px;margin-bottom:10px;padding-left:40px;'>" + $scope.organization.name + "授权</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<div class='col-sm-12'>" +
                    "<input type='text' class='form-control' placeholder='用户账号搜索' ng-model='search_key' ng-keyup='search_users_keyup($event)' />" +
                  "</div>" +
                "</div>" +
                "<table class='table' ng-show='!!search_users' style='margin-top:20px;'>" +
                  "<thead><th>账号</th><th>权限</th><th>操作</th></thead>" +
                  "<tbody>" +
                    "<tr ng-repeat='search_user in search_users | orderBy : name : incr' ng-init='search_user.role=\"delete\"'>" +
                      "<td>{{ search_user.name  }}</td>" +
                      "<td>" +
                        "<select class='form-control' ng-model='search_user.role'>" +
                          "<option value='modifier'>modifier</option>" +
                          "<option value='puller'>puller</option>" +
                          "<option value='viewer'>viewer</option>" +
                          "<option value='delete'>回收权限</option>" +
                        "</select>" +
                      "</td>" +
                      "<td>" +
                        "<button type='button' class='btn btn-danger' ng-click='authorize(search_user)'>授权</button>" +
                      "</td>" +
                    "</tr>" +
                  "</tbody>" +
                "</table>" +
              "</form>"
    var compileFn = $compile(msg);
    var $dom = compileFn($scope);
    var $sut = angular.element(document.getElementById('authorize-organization'));
    $sut.append($dom);
  };
  $scope.goto_project = function(project) {
    console.log("goto project", project);
    $state.go("dashboard.config.proj", { prid: project.id });
  }
})

.controller('ProjectCtrl', function ($scope, $compile, $state, $stateParams, $connection, $utils, $item_helper) {
  console.log('enter project controller');
  const prid = $stateParams.prid;

  $connection.get_project(prid).then(function(p) {
    console.log(p);
    $scope.project = p;
  }).catch(function(err) {
    console.log(err);
    $utils.error(err.msg, function() {
      if (code == -2) {
        $state.go('dashboard.index');
      } else {
        if ($stateParams.r == 'search') {
          $state.go('dashboard.config_search');
        } else {
          $state.go('dashboard.config.index');
        }
      }
    });
  });

  $scope.item = { "name": "", "visibility": "public", "type": "PLAIN" };
  $scope.new_item = {"name": "", "visibility": "public", "type": "PLAIN"};
  $scope.create_item = function() {
    $item_helper.create_item_for_project($scope, $compile);
  };
  $scope.update_project = function() {
    $utils.confirm("是否确认需要修改该项目?", function(ok) {
      if (ok) {
        let is_private = false;
        if ($scope.project.visibility == "private") {
          is_private = true;
        }
        $connection.update_project(prid, {"private": is_private}).then(function(ok) {
          $utils.success("已修改成功");
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.delete_project = function() {
    $utils.confirm("是否确认需要删除该项目?", function(ok) {
      if (ok) {
        $connection.delete_project(prid).then(function(ok) {
          $utils.success("删除成功", function() {
            $state.go('dashboard.config.org', {oid: $scope.project.parent_id});
          });
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.authorize_project = function() {
    $utils.dialog("<div id='authorize-project' style='padding-bottom:20px;'></div>", true);
    $scope.search_key = "";
    $scope.search_users = null;
    $scope.search_users_keyup = function(e) {
      var keycode = window.event ? e.keyCode : e.which;
      if(keycode==13){
        if ($scope.search_key == "") {
          $utils.error("搜索账号不能为空");
          return;
        }
        $connection.search_users($scope.search_key).then(function(users) {
          console.log(users);
          $scope.search_users = users;
        }).catch(default_error_handle($state, $utils));
      }
    };
    $scope.authorize = function(authorize_user) {
      if (authorize_user.role == "delete") {
        $utils.confirm("是否确定回收 " + authorize_user.name + " 的权限", function(ok) {
          if (ok) {
            $connection.cancel_project(prid, authorize_user.id).then(function(ok) {
              let privileges = $scope.project.privileges;
              for (let i = 0; i < privileges.length; i++) {
                if (authorize_user.id == privileges[i].user_id) {
                  privileges.splice(i, 1);
                  break;
                }
              }
              $utils.success("取消授权成功");
            }).catch(default_error_handle($state, $utils));
          }
        });
      } else {
        $utils.confirm("是否确定授予 " + authorize_user.name + " 的 " + authorize_user.role + " 权限?", function(ok) {
          if (ok) {
            $connection.authorize_project(prid, authorize_user.id, authorize_user.role).then(function(ok) {
              for (let i = 0; i < $scope.project.privileges.length; i++) {
                if ($scope.project.privileges[i].user_id == authorize_user.id) {
                  $scope.project.privileges[i].type = authorize_user.role;
                  $utils.success("授权成功");
                  return;
                }
              }
              $scope.project.privileges.push({
                "id": "0",
                "user_id": authorize_user.id,
                "user_name": authorize_user.name,
                "type": authorize_user.role
              });
              $utils.success("授权成功");
            }).catch(default_error_handle($state, $utils));
          }
        });
      }
    };
    var msg = "<form class='form-horizontal'>" +
                "<div class='form-group'>" +
                  "<div style='font-size:32px;margin-bottom:10px;padding-left:40px;'>" + $scope.project.name + "授权</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<div class='col-sm-12'>" +
                    "<input type='text' class='form-control' placeholder='用户账号搜索' ng-model='search_key' ng-keyup='search_users_keyup($event)' />" +
                  "</div>" +
                "</div>" +
                "<table class='table' ng-show='!!search_users' style='margin-top:20px;'>" +
                  "<thead><th>账号</th><th>权限</th><th>操作</th></thead>" +
                  "<tbody>" +
                    "<tr ng-repeat='search_user in search_users | orderBy : name : incr' ng-init='search_user.role=\"delete\"'>" +
                      "<td>{{ search_user.name  }}</td>" +
                      "<td>" +
                        "<select class='form-control' ng-model='search_user.role'>" +
                          "<option value='modifier'>modifier</option>" +
                          "<option value='puller'>puller</option>" +
                          "<option value='viewer'>viewer</option>" +
                          "<option value='delete'>回收权限</option>" +
                        "</select>" +
                      "</td>" +
                      "<td>" +
                        "<button type='button' class='btn btn-danger' ng-click='authorize(search_user)'>授权</button>" +
                      "</td>" +
                    "</tr>" +
                  "</tbody>" +
                "</table>" +
              "</form>"
    var compileFn = $compile(msg);
    var $dom = compileFn($scope);
    var $sut = angular.element(document.getElementById('authorize-project'));
    $sut.append($dom);
  };
  $scope.goto_parent = function() {
    $state.go("dashboard.config.org", {oid: $scope.project.parent_id});
  }
  $scope.goto_item = function(item) {
    console.log("goto item: ", item);
    $state.go("dashboard.config.item.index", {iid: item.id});
  }
})

.controller('ItemCtrl', function ($scope, $compile, $state, $stateParams, $connection, $utils, $item_helper) {
  console.log('enter item controller');
  const iid = $stateParams.iid;
  if (iid == null || typeof(iid) === 'undefined') {
    $utils.error("非法请求", function() {
      if ($stateParams.r == 'search') {
        $state.go('dashboard.config_search');
      } else {
        $state.go('dashboard.config.index');
      }
    });
    return;
  }

  $scope.item = { "name": "", "visibility": "", "type": "" };
  $scope.new_item =  {"name": "", "visibility": "public", "type": "PLAIN"};
  var __editor = $item_helper.item_display($scope);


  $scope.publish_item = function() {
    $utils.confirm("是否确认需要全量发布该配置项?", function(ok) {
      if (ok) {
        let is_private = false;
        if ($scope.item.visibility === "private") {
          is_private = true;
        }
        $connection.publish_item(iid, {"content": __editor.getValue(), "type": $scope.item.type, "private": is_private}).then(function(ok) {
          $utils.success("已发布成功");
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.gray_item = function() {
    console.log("goto gray item");
    $state.go('dashboard.config.item.gray', { oid: $stateParams.oid, prid: $scope.item.parent_id,  iid: iid });
  };
  $scope.version_item = function() {
    console.log("goto version item");
    $state.go('dashboard.config.item.version', { oid: $stateParams.oid, prid: $scope.item.parent_id,  iid: iid });
  };
  $scope.stats_item = function() {
    console.log("goto stats item");
    $state.go('dashboard.config.item.stats', { oid: $stateParams.oid, prid: $scope.item.parent_id,  iid: iid });
  };
  $scope.delete_item = function() {
    $utils.confirm("是否确认需要删除该配置项?", function(ok) {
      if (ok) {
        $connection.delete_item(iid).then(function(ok) {
          $utils.success("删除成功", function() {
            $state.go('dashboard.config.proj', { prid: $scope.item.parent_id });
          });
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.authorize_item = function() {
    $utils.dialog("<div id='authorize-item' style='padding-bottom:20px;'></div>", true);
    $scope.search_key = "";
    $scope.search_users = null;
    $scope.search_users_keyup = function(e) {
      var keycode = window.event ? e.keyCode : e.which;
      if(keycode==13){
        if ($scope.search_key == "") {
          $utils.error("搜索账号不能为空");
          return;
        }
        $connection.search_users($scope.search_key).then(function(users) {
          console.log(users);
          $scope.search_users = users;
        }).catch(default_error_handle($state, $utils));
      }
    };
    $scope.authorize = function(authorize_user) {
      if (authorize_user.role == "delete") {
        $utils.confirm("是否确定回收 " + authorize_user.name + " 的权限", function(ok) {
          if (ok) {
            $connection.cancel_item(iid, authorize_user.id).then(function(ok) {
              let privileges = $scope.item.privileges;
              for (let i = 0; i < privileges.length; i++) {
                if (authorize_user.id == privileges[i].user_id) {
                  privileges.splice(i, 1);
                  break;
                }
              }
              $utils.success("取消授权成功");
            }).catch(default_error_handle($state, $utils));
          }
        });
      } else {
        $utils.confirm("是否确定授予 " + authorize_user.name + " 的 " + authorize_user.role + " 权限?", function(ok) {
          if (ok) {
            $connection.authorize_item(iid, authorize_user.id, authorize_user.role).then(function(ok) {
              for (let i = 0; i < $scope.item.privileges.length; i++) {
                if ($scope.item.privileges[i].user_id == authorize_user.id) {
                  $scope.item.privileges[i].type = authorize_user.role;
                  $utils.success("授权成功");
                  return;
                }
              }
              $scope.item.privileges.push({
                "id": "0",
                "user_id": authorize_user.id,
                "user_name": authorize_user.name,
                "type": authorize_user.role
              });
              $utils.success("授权成功");
            }).catch(default_error_handle($state, $utils));
          }
        });
      }
    };
    var msg = "<form class='form-horizontal'>" +
                "<div class='form-group'>" +
                  "<div style='font-size:32px;margin-bottom:10px;padding-left:40px;'>" + $scope.item.name + "授权</div>" +
                "</div>" +
                "<div class='form-group'>" +
                  "<div class='col-sm-12'>" +
                    "<input type='text' class='form-control' placeholder='用户账号搜索' ng-model='search_key' ng-keyup='search_users_keyup($event)' />" +
                  "</div>" +
                "</div>" +
                "<table class='table' ng-show='!!search_users' style='margin-top:20px;'>" +
                  "<thead><th>账号</th><th>权限</th><th>操作</th></thead>" +
                  "<tbody>" +
                    "<tr ng-repeat='search_user in search_users | orderBy : name : incr' ng-init='search_user.role=\"delete\"'>" +
                      "<td>{{ search_user.name  }}</td>" +
                      "<td>" +
                        "<select class='form-control' ng-model='search_user.role'>" +
                          "<option value='modifier'>modifier</option>" +
                          "<option value='puller'>puller</option>" +
                          "<option value='viewer'>viewer</option>" +
                          "<option value='delete'>回收权限</option>" +
                        "</select>" +
                      "</td>" +
                      "<td>" +
                        "<button type='button' class='btn btn-danger' ng-click='authorize(search_user)'>授权</button>" +
                      "</td>" +
                    "</tr>" +
                  "</tbody>" +
                "</table>" +
              "</form>"
    var compileFn = $compile(msg);
    var $dom = compileFn($scope);
    var $sut = angular.element(document.getElementById('authorize-item'));
    $sut.append($dom);
  };
  $scope.goto_parent = function() {
    $state.go("dashboard.config.proj", {prid: $scope.item.parent_id});
  };
  $scope.create_item_based_on_current = function() {
    $item_helper.create_item_based_on_current($scope, $compile);
  };
})

.controller('GrayItemCtrl', function ($scope, $compile, $state, $stateParams, $connection, $utils, $item_helper) {
  console.log('enter gray item controller');
  const iid = $stateParams.iid;
  if (iid == null || typeof(iid) === 'undefined') {
    $utils.error("非法请求", function() {
      $state.go('dashboard.config.index');
    });
    return;
  }

  $scope.item = { "name": "", "visibility": "", "type": "" };
  $scope.new_item =  {"name": "", "visibility": "public", "type": "PLAIN"};
  var __editor = $item_helper.item_display($scope);

  $scope.publish_item = function() {
    $utils.confirm("是否确认需要全量发布该配置项?", function(ok) {
      if (ok) {
        let is_private = false;
        if ($scope.item.visibility == "private") {
          is_private = true;
        }
        $connection.publish_item(iid, {"content": __editor.getValue(), "type": $scope.item.type, "private": is_private}, false).then(function(ok) {
          $utils.success("已发布成功");
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.publish_gray_item = function() {
    $utils.confirm("是否确认需要灰度发布该配置项?", function(ok) {
      if (ok) {
        let is_private = false;
        if ($scope.item.visibility == "private") {
          is_private = true;
        }
        $connection.publish_item(iid, {"content": __editor.getValue(), "type": $scope.item.type, "private": is_private}, true).then(function(ok) {
          $utils.success("已发布成功");
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.delete_item = function() {
    $utils.confirm("是否确认需要删除该灰度配置项?", function(ok) {
      if (ok) {
        $connection.delete_item(iid, true).then(function(ok) {
          $utils.success("删除成功", function() {
            const iid = $stateParams.iid;
            $state.go('dashboard.config.item.index', { iid: iid });
          });
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.goto_parent = function() {
    const iid = $stateParams.iid;
    $state.go("dashboard.config.item.index", { iid: iid });
  };
})

.controller('VersionCtrl', function ($scope, $state, $stateParams, $location, $connection, $utils) {
  console.log('enter item version controller');
  const iid = $stateParams.iid;
  if (iid == null || typeof(iid) === 'undefined') {
    $utils.error("非法请求", function() {
      $state.go('dashboard.config.index');
    });
    return;
  }

  $scope.page = { offset: parseInt($stateParams.offset) || 0 };
  $connection.get_item_versions(iid, $scope.page.offset).then(function(page) {
    console.log(page);
    $location.search("offset", page.offset);
    $scope.page = page;
  }).catch(default_error_handle($state, $utils));

  $scope.get_prev_versions = function() {
    var offset = $scope.page.offset || 0;
    offset = Math.floor(offset / 10) * 10 - 10;
    $connection.get_item_versions(iid, offset).then(function(page) {
      $location.search("offset", page.offset);
      $scope.page = page;
    }).catch(default_error_handle($state, $utils));
  };
  $scope.get_next_versions = function() {
    var offset = $scope.page.offset || 0;
    offset = Math.floor(offset / 10) * 10 + 10;
    $connection.get_item_versions(iid, offset).then(function(page) {
      $location.search("offset", page.offset);
      $scope.page = page;
    }).catch(default_error_handle($state, $utils));
  };
  $scope.rollback = function(version) {
    $utils.confirm("是否将使用版本 " + version.id + " 进行回滚?", function(ok) {
      if (ok) {
        $connection.rollback(iid, version.id).then(function(current) {
          $utils.success("回滚成功", function() {
            const iid = current.id || $stateParams.iid;
            $state.go('dashboard.config.item.index', { iid: iid });
          });
        }).catch(default_error_handle($state, $utils));
      }
    });
  };
  $scope.goto_parent = function() {
    const iid = $stateParams.iid;
    $state.go("dashboard.config.item.index", { iid: iid });
  }
})

.controller('StatsCtrl', function ($scope, $state, $stateParams, $location, $connection, $utils, $interval) {
  console.log('enter item controller');
  const iid = $stateParams.iid;
  if (iid == null || typeof(iid) === 'undefined') {
    $utils.error("非法请求", function() {
      $state.go('dashboard.config.index');
    });
    return;
  }

  $scope.$on('$destroy', function() {
    console.log("stats controller destroy");
    if (!!$scope.timer) {
      $interval.cancel($scope.timer);
    }
  });

  const ascii = '97531';
  var default_colors = [];
  for (var i = 0; i < ascii.length; i++) {
    default_colors.push('#00' + ascii[i] + ascii[i] + '00');
  }
  for (var i = 0; i < ascii.length; i++) {
    default_colors.push('#0000' + ascii[i] + ascii[i]);
  }
  for (var i = 0; i < ascii.length; i++) {
    default_colors.push('#' + ascii[i] + ascii[i] + '0000');
  }

  var last_search_key = '';
  var last_search_param = 'version';

  $scope.search_key = '';
  $scope.search_param = 'version';
  $scope.viewModel = 'airscape';
  $scope.refreshModel = 'auto';
  $scope.coloredModel = 'version';

  $scope.$watch('coloredModel', function() {
    colored_search_result($scope.search_result || [], $scope.coloredModel);
  });

  function colored_search_result(data, colorby) {
    var colors = {};
    if (colorby === "version") {
      data.forEach(item => {
        if (!item.grey) {
          colors[item.iver] = "#00ff00";
        }
      });
      var i = 0;
      for (var key in colors) {
        colors[key] = default_colors[i % default_colors.length];
        i = i + 1;
      }
      data.forEach(item => {
        item.color = (item.grey ? "#808080" : colors[item.iver]);
      });
    } else if (colorby == "lastversion") {
      data.forEach(item => {
        if (!item.grey) {
          colors[item.lver] = "#00ff00";
        }
      });
      var i = 0;
      for (var key in colors) {
        colors[key] = default_colors[i % default_colors.length];
        i = i + 1;
      }
      data.forEach(item => {
        item.color = colors[item.lver];
      });
    } else if (colorby === "ip") {
      data.forEach(item => {
        colors[item.ip] = "#00ff00";
      });
      var i = 4;
      for (var key in colors) {
        colors[key] = default_colors[i % default_colors.length];
        i = i + 1;
      }
      data.forEach(item => {
        item.color = colors[item.ip];
      });
    } else if (colorby === "instanceid") {
      data.forEach(item => {
        colors[item.ctype + item.cid] = "#00ff00";
      });
      var i = 8;
      for (var key in colors) {
        colors[key] = default_colors[i % 15];
        i = i + 1;
      }
      data.forEach(item => {
        item.color = colors[item.ctype + item.cid];
      });
    } else if (colorby === "clientversion") {
      data.forEach(item => {
        colors[item.cver] = "#00ff00";
      });
      var i = 12;
      for (var key in colors) {
        colors[key] = default_colors[i % default_colors.length];
        i = i + 1;
      }
      data.forEach(item => {
        item.color = colors[item.cver];
      });
    }
    return data;
  }

  function fill_search_result(item, search_key, search_param) {
    let search_result = [];
    if (!search_key) {
      item.stats.forEach(stat => { search_result.push(stat); });
    } else {
      if (search_param == "version") {
        item.stats.forEach(stat => {
          if (stat.iver == search_key) {
            search_result.push(stat);
          }
        });
      } else if (search_param == "lastversion") {
        item.stats.forEach(stat => {
          if (stat.lver == search_key) {
            search_result.push(stat);
          }
        });
      } else if (search_param == "ip") {
        item.stats.forEach(stat => {
          if (stat.ip == search_key) {
            search_result.push(stat);
          }
        });
      } else if (search_param == "clientversion") {
        item.stats.forEach(stat => {
          if (stat.cver == search_key) {
            search_result.push(stat);
          }
        });
      } else if (search_param == "instanceid") {
        item.stats.forEach(stat => {
          const t = stat.ctype + "-" + stat.cid;
          if (t.indexOf(search_key) > -1) {
            search_result.push(stat);
          }
        });
      }
    }
    return search_result;
  }

  var load_stats = function () {
    console.log("load stats");
    $connection.get_item_stats(iid).then(function(item) {
      $scope.item = item;
      let search_result = fill_search_result(item, last_search_key, last_search_param);
      $scope.search_result = colored_search_result(search_result, $scope.coloredModel);
      last_search_key = $scope.search_key;
      last_search_param = $scope.search_param;
    }).catch(default_error_handle($state, $utils));
  };

  $scope.$watch('refreshModel', function() {
    if ($scope.refreshModel == 'auto') {
      if (!$scope.timer) {
        $scope.timer = $interval(function() {
          load_stats();
        }, 60000);
      }
    } else {
      if (!!$scope.timer) {
        $interval.cancel($scope.timer);
        $scope.timer = null;
      }
    }
  });
  if (!$scope.timer) {
    $scope.timer = $interval(function() {
      load_stats();
    }, 60000);
  }

  load_stats();

  $scope.search = function(e) {
    var keycode = window.event ? e.keyCode : e.which;
    if(keycode != 13) return;
    if ($scope.search_key == last_search_key &&
        $scope.search_param == last_search_param) return;
    let search_result = fill_search_result($scope.item, $scope.search_key, $scope.search_param);
    $scope.search_result = colored_search_result(search_result, $scope.coloredModel);
    last_search_key = $scope.search_key;
    last_search_param = $scope.search_param;
  };

  $scope.goto_parent = function() {
    const iid = $stateParams.iid;
    $state.go("dashboard.config.item.index", { iid: iid });
  };
})

.controller('APICtrl', function($scope, $state, $connection, $utils) {
  console.log("enter APICtrl");
  $connection.get_api_document().then(function(doc) {
    document.getElementById("api-content").innerHTML = marked(doc)
  }).catch(default_error_handle($state, $utils));
})

.filter('visibility', function () {
  return function (name) {
    if (name == 'private') return '私有';
    if (name == 'public') return '公开';
    return '未知';
  };
})

.filter('param', function () {
  return function (name) {
    if (name == 'version') return '当前版本';
    if (name == 'lastversion') return '上一版本';
    if (name == 'ip') return 'IP';
    if (name == 'instanceid') return '实例号';
    if (name == 'clientversion') return '客户端版本';
    return 'UNKNOWN';
  };
})

.filter('uppercase', function () {
  return function (name) {
    console.log("uppercase: ", name);
    return name.toUpperCase();
  }
})

