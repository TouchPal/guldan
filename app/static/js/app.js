/**
*  Module
*
* Description
*/
angular.module('guldan', ['ngAnimate', 'ui.router', 'ui.bootstrap', 'ui.ace', 'guldan.controllers', 'guldan.services'])

.config(function($stateProvider, $urlRouterProvider) {
	$stateProvider.state('dashboard', {
		url: '/dashboard',
		templateUrl: 'templates/dashboard.html',
		controller: 'DashboardCtrl'
	})
  .state('dashboard.index', {
    url: '/index',
    template: '<div ng-show="!!user">' +
                '<h1>用户基本信息</h1>' +
                '<div style="height: 40px"></div>' +
                '<table class="table table-bordered">' +
                  '<thead><tr><th>用户ID</th><th>用户名</th><th>用户HASH</th></tr></thead>' +
                  '<tbody>' +
                    '<tr><td>{{ user.id }}</td><td>{{ user.name }}</td><td>{{ user.hash }}</td></tr>' +
                  '</tbody>' +
                '</table>' +
              '</div>' +
              '<h1 ng-show="!user" style="text-align:center;">Guldan配置管理中心</h1>',
  })
	.state('dashboard.reg', {
		url: '/reg',
		templateUrl: 'templates/reg.html',
		controller: 'RegCtrl'
	})
  .state('dashboard.users', {
    url: '/users',
    templateUrl: 'templates/users.html',
    controller: 'UsersCtrl',
  })
  .state('dashboard.config', {
    url: '/config',
    template: '<div ui-view="" />'
  })
  .state('dashboard.config.index', {
    url: '/index',
    templateUrl: 'templates/config/index.html',
    controller: 'ConfigManageCtrl'
  })
  .state('dashboard.config.org', {
    url: '/organization/:oid?r',
    templateUrl: 'templates/config/organization/index.html',
    controller: 'OrganizationCtrl'
  })
  .state('dashboard.config.proj', {
    url: '/project/:prid?r',
    templateUrl: 'templates/config/organization/project/index.html',
    controller: 'ProjectCtrl'
  })
  .state('dashboard.config.item', {
    url: '/item',
    template: '<div ui-view="" />'
  })
  .state('dashboard.config.item.index', {
    url: '/:iid?r',
    templateUrl: 'templates/config/organization/project/item/index.html',
    controller: 'ItemCtrl'
  })
  .state('dashboard.config.item.gray', {
    url: '/:iid/gray',
    templateUrl: 'templates/config/organization/project/item/gray.html',
    controller: 'GrayItemCtrl'
  })
  .state('dashboard.config.item.version', {
    url: '/:iid/version?offset',
    templateUrl: 'templates/config/organization/project/item/version.html',
    controller: 'VersionCtrl',
    reloadOnSearch: false
  })
  .state('dashboard.config.item.stats', {
    url: '/:iid/stats',
    templateUrl: 'templates/config/organization/project/item/stats.html',
    controller: 'StatsCtrl'
  })
  .state('dashboard.config_search', {
    url: "/config_search?key",
    templateUrl: 'templates/config_search.html',
    controller: 'ConfigSearchCtrl',
    reloadOnSearch: false
  })
  .state('dashboard.history_operation', {
    url: '/history_operation?key',
    templateUrl: 'templates/history_operation.html',
    controller: 'HistoryOperationCtrl',
    reloadOnSearch: false
  })
  .state('dashboard.api', {
    url: '/api',
    template: '<div style="margin-left:40px" <div id="api-content"></div>',
    controller: 'APICtrl'
  })

	$urlRouterProvider.otherwise('/dashboard/index');
})
.run(['$rootScope', '$state', function($rootScope, $state){
  $rootScope.$on('$locationChangeStart', function (event, current, previous) {
    console.log("Previous URL: " +previous);
  });
	$rootScope.$state = $state;
}]);
