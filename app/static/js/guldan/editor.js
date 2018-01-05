function extend(Child, Parent) {
  var F = function () {
  };

  F.prototype = new Parent();
  Child.prototype = new F();
  Child.prototype.constructor = Child;
  Child.uber = Parent.prototype;
}

function GuldanEditor(scope) {
  this.editor = null;
  this.scope = scope;

  this.initGuldanEditor = function (ace_editor) {
    ace_editor.setTheme('ace/theme/tomorrow');
    ace_editor.renderer.setShowGutter(true);
    ace_editor.getSession().setMode('ace/mode/text');
    this.editor = ace_editor;

    return this.editor;
  };
  var that = this;
  this.changeEditorMode = function (itemtype) {
    const type = itemtype.toUpperCase();
    if (type === "JSON") {
      that.editor.getSession().setMode('ace/mode/json');
    } else if (type === "XML") {
      that.editor.getSession().setMode('ace/mode/xml');
    } else if (type === "YAML") {
      that.editor.getSession().setMode('ace/mode/yaml');
    } else {
      that.editor.getSession().setMode('ace/mode/text');
    }
  };

  this.watch_for_item_type_change = function (item_type_model) {
    this.scope.$watch(item_type_model, this.changeEditorMode);
  };

  this.getValue = function () {
    return that.editor.getValue();
  }
}

function ItemDisplayEditor(scope, connection, itemId, itemErrorHandler) {
  ItemDisplayEditor.uber.constructor.call(this, scope);
  this.itemId = itemId;
  this.connection = connection;
  this.itemErrorHandler = itemErrorHandler;

  this.fetch_item_and_set_editor_value = function () {
    var that = this;
    this.connection.get_item(this.itemId, true).then(function (item) {
      console.log(item);
      that.scope.item = item;
      that.editor.setValue(item.content, -1);
    }).catch(that.itemErrorHandler);
  };

  this.guldanEditorLoaded = function (ace_editor) {
    ItemDisplayEditor.prototype.initGuldanEditor.call(this, ace_editor);
    ItemDisplayEditor.prototype.watch_for_item_type_change.call(this, 'item.type');
    this.fetch_item_and_set_editor_value();
  }
}

function ItemCreateForProjectEditor(scope, connection, project) {
  ItemCreateForProjectEditor.uber.constructor.call(this, scope);
  this.connection = connection;
  this.project = project;

  this.guldanEditorLoaded = function (ace_editor) {
    ItemCreateForProjectEditor.prototype.initGuldanEditor.call(this, ace_editor);
    ItemCreateForProjectEditor.prototype.watch_for_item_type_change.call(this, 'new_item.type');
  };

  this.createNewItem = function (newItem, successCallback, errorCallback) {
    var isPrivate = newItem.visibility === 'private' ? 'true' : 'false';
    this.connection.create_item(newItem.prid, newItem.name, this.editor.getValue(), newItem.type, isPrivate).then(function (item) {
      successCallback(item)
    }).catch(errorCallback);
  };
}

function ItemCreateBasedOnExistingItemEditor(scope, connection, currentItem) {
  ItemCreateBasedOnExistingItemEditor.uber.constructor.call(this, scope);
  this.connection = connection;
  this.currentItem = currentItem;

  this.guldanEditorLoaded = function (ace_editor) {
    ItemCreateBasedOnExistingItemEditor.prototype.initGuldanEditor.call(this, ace_editor);
    ItemCreateBasedOnExistingItemEditor.prototype.watch_for_item_type_change.call(this, 'new_item.type');
    this.setEditorBasedOnCurrentItem();
  };

  this.setEditorBasedOnCurrentItem = function () {
    let names = this.currentItem.name.split(".");
    this.scope.new_item.name = names[names.length - 1];
    this.scope.new_item.type = currentItem.type;

    this.editor.setValue(currentItem.content, -1);
  };

  this.createNewItem = function (newItem, successCallback, errorCallback) {
    var isPrivate = newItem.visibility === 'private' ? 'true' : 'false';
    this.connection.create_item(newItem.prid, newItem.name, this.editor.getValue(), newItem.type, isPrivate).then(function (item) {
      successCallback(item);
    }).catch(errorCallback);
  }
}


extend(ItemDisplayEditor, GuldanEditor);
extend(ItemCreateForProjectEditor, GuldanEditor);
extend(ItemCreateBasedOnExistingItemEditor, GuldanEditor);
