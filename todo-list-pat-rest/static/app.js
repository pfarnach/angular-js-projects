/* -----------------
By Pat Farnach
www.patfarnach.com
------------------- */

var app = angular.module("todo", []);

app.controller("MainCtrl", function($scope){
	$scope.selectedTab = 1;
});

app.controller("InlineEditorController", function($scope){
	$scope.inlineEdit = false;
	$scope.inlineText = "Click here to edit.";
	$scope.toggleInlineEdit = function (){
		$scope.inlineEdit = !$scope.inlineEdit;
	};
});

app.controller("TodoList", function($scope, $http){

	// for order preference
	$scope.orderPref = "id";
	$scope.selectedHeader = "id";
	$scope.ascending = true;

	// orders how entry rows are displayed (toggles between asc and desc order)
	$scope.selectOrder = function(pref) {

		$scope.selectedHeader = pref;
		if (pref == $scope.orderPref) {
			$scope.orderPref = "-" + pref;
			$scope.ascending = false;
		} else {
			$scope.orderPref = pref;
			$scope.ascending = true;
		}

	};

	// live search variable has to be set to empty string to start off
	$scope.query = "";
	$scope.todolist = [];
	fetch_list();

	// fetch list from database run by bottle.py
	function fetch_list() {
		$http.get('/get-todo-list').
			success(function(data, status, headers, config) {
				// this callback will be called asynchronously
				// when the response is available
				console.log(data);
				create_todolist(data);
			}).
			error(function(data, status, headers, config) {
				// called asynchronously if an error occurs
				// or server returns response with an error status.
			});
	}

	// generate todo list from json
	function create_todolist(data) {
		$scope.todolist = [];
		for (var i = 0; i < data.length; i++) {
			$scope.todolist.push({
				id: data[i]['id'],
				name: data[i]['task'],
				due_date: data[i]['due_date'],
				done: data[i]['done'],
				db_id: data[i]['db_id']
			});
		}
	}


	// add
	$scope.enableAdd = false;
	$scope.newEntry = {id: $scope.todolist.length+1, name: "", due_date: "", done: false};

	// shows add form, disables edit form
	$scope.enableAddEvent = function() {
		$scope.enableEdit = false;
		$scope.enableAdd = true;
	};

	// disables add event
	$scope.disableAddEvent = function() {
		$scope.enableAdd = false;
	};

	// takes ng-model form info appends it to todolist, then creates a blank "form"
	$scope.addEvent = function(newEntry) {
		newEntry.id =  $scope.todolist.length + 1;
		add_entry_db(newEntry);
		$scope.enableAdd = false;
		$scope.newEntry = {name: "", due_date: "", done: false};
	};

	function add_entry_db(newEntry) {
		$http.post('/add-entry', newEntry).
			success(function(data, status, headers, config) {
				console.log(data);
				create_todolist(data);
			}).
			error(function(data, status, headers, config) {
				alert( "failure message: " + JSON.stringify({data: data}));
			});
	}


	// default edit status
	$scope.enableEdit = false;
	$scope.editedIndex = null;

	// shows edit form, hides add form, and displays current info in edit form (w/o modifying todolist)
	$scope.enableEditEvent = function(entry) {
		$scope.editedEntry = angular.copy(entry);
		$scope.enableAdd = false;
		$scope.enableEdit = true;
		$scope.editedIndex = $scope.todolist.indexOf(entry);
	};

	$scope.updateEntry = function(editedEntry) {
		console.log(editedEntry.db_id);
		console.log(editedEntry.name);
		console.log(editedEntry.due_date);
		$http.put('/update-entry-text', {'db_id': editedEntry.db_id, 'task': editedEntry.name, 'due_date': editedEntry.due_date }).
			success(function(data, status, headers, config){
				create_todolist(data);
			}).
			error(function(data, status, headers, config){
				console.log("Error in put request for update entry text");
			});
		$scope.enableEdit = false;
	};

	$scope.cancelEditing = function() {
		$scope.enableEdit = false;
	};


	// remove 
	$scope.removeEntry = function(entry) {
		$http.delete('/delete-entry', {params: {'priority': entry['id']}}).
			success(function(data, status, headers, config){
				create_todolist(data);
			}).
			error(function(data, status, headers, config){
				console.log("Error in delete request");
			});
		// $scope.todolist.splice($scope.todolist.indexOf(entry), 1);
		$scope.enableEdit = false;
		$scope.enableAdd = false;
	};

	// mark as done/undone
	$scope.updateDone = function(entry) {
		var done = entry.done ? false : true;
		$http.put('/update-done-field', {'priority': entry.id, 'done': done }).
			success(function(data, status, headers, config){
				create_todolist(data);
			}).
			error(function(data, status, headers, config){
				console.log("Error in put request for mark-as-done");
			});
	};

	// resassign IDs so they're consistent
	$scope.reassignID = function() {
		for (var i = 0; i < $scope.todolist.length; i++) {
			$scope.todolist[i].id = i + 1;
		}
	};

	function updatePriority(new_id, db_id) {
		$http.put('/update-priority-field', {'new_pr': new_id, 'db_id': db_id }).
			success(function(data, status, headers, config){
				create_todolist(data);
			}).
			error(function(data, status, headers, config){
				console.log("Error in put request for mark-as-done");
			});
	}

	// change priority
	$scope.priorityUp = function(entry) {

		temp_current_id = entry.id;
		// if entry isn't already highest on list
		if (temp_current_id > 1) {

			// have to switch ID with entry one "up" on priority list
			targetID = temp_current_id - 1;
			temp_list = angular.copy($scope.todolist);

			// loop through list to find the entry that is going down a spot and then lower its priority
			for (var i = 0; i < temp_list.length; i++) {
				if (temp_list[i].id === targetID) {
					temp_list[i].id += 1;
					updatePriority(temp_list[i].id, temp_list[i].db_id);
					break;
				}
			}

			// move current entry up
			temp_current_id -= 1;
			updatePriority(temp_current_id, entry.db_id);
		}
	};

	$scope.priorityDown = function(entry) {

		// find lowest priority -- that'll be max to set limit on moving down priority (ie. can't go lower than current lowest priority)
		$scope.todolist.sort(function(a,b) {
			return b.id - a.id;
		});

		max_id = $scope.todolist[0].id;

		temp_current_id = entry.id;
		// if entry isn't already highest on list
		if (entry.id < max_id) {

			// have to switch ID with entry one "up" on priority list
			targetID = temp_current_id + 1;
			temp_list = angular.copy($scope.todolist);

			// loop through list to find the entry that is going down a spot and then lower its priority
			for (var i = 0; i < temp_list.length; i++) {
				if (temp_list[i].id === targetID) {
					temp_list[i].id -= 1;
					updatePriority(temp_list[i].id, temp_list[i].db_id);
					break;
				}
			}

			// move current entry up
			temp_current_id += 1;
			updatePriority(temp_current_id, entry.db_id);
		}
	};

});



