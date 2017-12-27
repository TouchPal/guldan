// var SERVICE_ADDR = "http://localhost:8080";
var SERVICE_ADDR = "";

if (!!bootbox) {
  bootbox.setDefaults({
    size: "small",
    locale: "zh_CN",
    closeButton: false
  });
  bootbox.setMessage = function(dialog, message) {
    dialog.find(".bootbox-body").html(message);
  };
}

function _clone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

var whoami = null;

function get_whoami() {
  return whoami;
}

function error_handle(q) {
  return function(err) {
    if (!!err.code) {
      q.reject(err);
    } else {
      q.reject({"code": -1, "msg": err.statusText || err});
    }
  }
}

angular.module('guldan.services', [])

.factory('$connection', ['$http', '$q', function($http, $q){
  return {
    me: function() {
      return get_whoami();
    },
    islogin: function () {
      var q = $q.defer();
      if (!!whoami) {
        q.resolve(get_whoami());
      } else {
        $http.get(SERVICE_ADDR + '/api/islogin').success(function(result) {
          whoami = result.data;
          return q.resolve(get_whoami());
        }).error(error_handle(q));
      }
      return q.promise;
    },
    reg: function (user) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/register', { name: user.name, password: user.password }).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    login: function (user) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/login', {name: user.name, password: user.password}).success(function(result) {
        whoami = result.data;
        q.resolve(whoami);
      }).error(error_handle(q));
      return q.promise;
    },
    logout: function () {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/logout').success(function (result) {
        whoami = null;
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    modify_profile: function (uid, password) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/user/' + uid, { "new_password": password }).success(function (result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    search_users: function (search_key) {
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/users?q=' + search_key).success(function(result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    list_organization: function() {
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/org').success(function (result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    create_organization: function(name, is_private) {
      var q = $q.defer();
      $http.put(SERVICE_ADDR + '/api/org', {"name": name, "private": is_private}).success(function(result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    delete_organization: function(oid) {
      var q = $q.defer();
      $http.delete(SERVICE_ADDR + '/api/org/' + oid).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    update_organization: function(oid, data) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/org/' + oid, data).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    get_organization: function(id) {
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/org/' + id).success(function(result) {
        if (!result.data.projects) {
          result.data.projects = [];
        }
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    authorize_organization: function(oid, uid, type) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/org/' + oid + '/authorize',
          {"user_id": uid, "type": type}).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    cancel_organization: function(oid, uid) {
      var q = $q.defer();
      $http.delete(SERVICE_ADDR + '/api/org/' + oid + '/authorize/' + uid).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    create_project: function(oid, name, is_private) {
      var q = $q.defer();
      $http.put(SERVICE_ADDR + '/api/project', {"parent_id": oid, "name": name, "private": is_private}).success(function(result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    delete_project: function(prid) {
      var q = $q.defer();
      $http.delete(SERVICE_ADDR + '/api/project/' + prid).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    update_project: function(prid, data) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/project/' + prid, data).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    get_project: function(id) {
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/project/' + id).success(function(result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    authorize_project: function(prid, uid, type) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/project/' + prid + '/authorize',
          {"user_id": uid, "type": type}).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    cancel_project: function(prid, uid) {
      var q = $q.defer();
      $http.delete(SERVICE_ADDR + '/api/project/' + prid + '/authorize/' + uid).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    create_item: function(prid, name, content, type, is_private, gray) {
      gray = !!gray || false;
      var q = $q.defer();
      $http.put(SERVICE_ADDR + '/api/item?grey=' + gray,
        {"parent_id": prid, "name": name, "content": content, "type": type, "private": is_private}).success(function(result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    delete_item: function(iid, gray) {
      gray = !!gray || false;
      var q = $q.defer();
      $http.delete(SERVICE_ADDR + '/api/item/' + iid + '?grey=' + gray).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    publish_item: function(iid, data, gray) {
      gray = !!gray || false;
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/item/' + iid + '?grey=' + gray, data).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    get_item: function(id, gray) {
      gray = !!gray || false;
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/item/' + id + '?grey=' + gray).success(function(result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    authorize_item: function(iid, uid, type) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/item/' + iid + '/authorize',
          {"user_id": uid, "type": type}).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    cancel_item: function(iid, uid) {
      var q = $q.defer();
      $http.delete(SERVICE_ADDR + '/api/item/' + iid + '/authorize/' + uid).success(function(result) {
        q.resolve(true);
      }).error(error_handle(q));
      return q.promise;
    },
    get_item_stats: function(iid) {
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/item/' + iid + '/stats').success(function(result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    get_item_versions: function(iid, offset) {
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/item/' + iid + '/versions?limit=10&order=desc&offset=' + offset).success(function(result) {
        let data = result.data;
        var page = {
          has_prev: offset != 0,
        has_next: offset + data.versions.length != data.total,
        offset: offset,
        versions: data.versions,
        };
        q.resolve(page);
      }).error(error_handle(q));
      return q.promise;
    },
    rollback: function(iid, version) {
      var q = $q.defer();
      $http.post(SERVICE_ADDR + '/api/item/' + iid + '/versions/rollback?version_id=' + version).success(function(result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    search_resources: function(key) {
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/resource/search?q=' + key).success(function (result) {
        q.resolve(result.data);
      }).error(error_handle(q));
      return q.promise;
    },
    search_audits: function(key, offset) {
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/api/audit/search?limit=10&offset=' +
          offset + '&q=' + key).success(function (result) {
        let data = result.data;
        var page = {
          search_key: key,
          has_prev: offset != 0,
          has_next: offset + data.audits.length != data.total,
          offset: offset,
          audits: data.audits,
        };
        q.resolve(page);
      }).error(error_handle(q));
      return q.promise;
    },
    get_api_document: function() {
      console.log("get api document");
      var q = $q.defer();
      $http.get(SERVICE_ADDR + '/API.md').success(function (result) {
        q.resolve(result);
      }).error(error_handle(q));
      return q.promise;
    },
  };
}])

.factory('$shared', [function(){
  var shared = {}
  return {
    get: function(key) {
      return shared[key];
    },
    set: function(key, value) {
      shared[key] = value;
    },
    remove: function(key) {
      shared[key] = undefined;
    }
  }
}])

.factory('$parent', [function(){
  let parents = [];
  return {
    push: function (path) {
      parents.push(path);
    },
    pop: function () {
      return parents.pop();
    }
  };
}])

.factory('$utils', [function(){
  return {
    error: function(message, callback) {
      bootbox.alert(message, callback);
    },
    success: function(message, callback, large) {
      if (!!large) {
        bootbox.alert({message: message, callback: callback, size: 'large'});
      } else {
        bootbox.alert(message, callback);
      }
    },
    loading: function(message, callback) {
      bootbox.dialog({ message: message });
    },
    confirm: function(message, callback, large) {
      if (!!large) {
        bootbox.confirm({message: message, callback: callback, size: 'large'});
      } else {
        bootbox.confirm({message: message, callback: callback});
      }
    },
    prompt: function(message, callback) {
      bootbox.prompt(message, callback);
    },
    dialog: function(message, large) {
      if (!!large) {
        bootbox.dialog({message: message, closeButton: true, size: 'large'});
      } else {
        bootbox.dialog({message: message, closeButton: true});
      }
    },
    clone: function(o) {
      return _clone(o);
    }
  };
}]);

