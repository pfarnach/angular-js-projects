
// Angular.js 1.3.14
var app = angular.module('photoviewer', ['angularFileUpload']);

// changes Angular's template handlebars to not conflict with jinja2 coming from backend
app.config(function($interpolateProvider) {
	$interpolateProvider.startSymbol('{[{');
	$interpolateProvider.endSymbol('}]}');
});

app.run(function($rootScope) {
    $rootScope.photos = [];
});

// fetches photos and displays them on individual album pages
app.controller('PhotoDisplayController', function($rootScope, $scope, $http){
	
	$scope.query = "";

	// fetch and display photos
	$scope.fetchphotos = function(query_string) {
		$http.get(query_string).
			success(function(data, status, headers, config) {
				if (!data.length) {
					$rootScope.photos = [];
				} else {
					$rootScope.photos = data;
					console.log(data);
				}
			}).
			error(function(data, status, headers, config) {
				console.log('AJAX request error');
			});
	};

	var album_id = document.getElementById("photo-displayer").getAttribute('data-album-id');
	var album_name = document.getElementById("photo-displayer").getAttribute('data-album-name');

	var query_string = '';

	// determine if we should get all of the photos or just photos of a particular album
	if (album_id === null || album_name === null) {
		query_string = '/photos';
		$scope.fetchphotos(query_string);
	} else {
		query_string = ('/albums/view?id=' + album_id +'&name=' + album_name);
		$scope.fetchphotos(query_string);
	}

	// delete photos
	$scope.delete_photo = function(photo_id) {

		$http.delete('/delete-photo', {params: {'photo_id': photo_id}}).
			success(function(data, status, headers, config){

				if (!data['success']) {
					console.log("Photo ID did not match photo in database.");

				} else if (data['success']) {

					var photos = angular.copy($rootScope.photos);

					// iterate through photos to find one that was just deleted and remove it from $scope
					for (var i=0; i < photos.length; i++) {
						if (photos[i]['photo_id'] === photo_id) {
							photos.splice(i, i+1);
							break;
						}
					}
					$rootScope.photos = photos;

				}
			}).
			error(function(data, status, headers, config){
				console.log(data);
			});
	};

	// image display credit: https://stackoverflow.com/questions/27211799/angular-ng-repeat-add-bootstrap-row-every-3-or-4-cols
});

// custom $upload service and progress bar direct via https://github.com/danialfarid/angular-file-upload
app.controller('UploadController', ['$rootScope', '$scope', '$upload', function ($rootScope, $scope, $upload) {

	$scope.photo = {};
	$scope.selectedFile = [];
	// $scope.uploadProgress = 0;
	$scope.success_alert = false;
	$scope.password_alert = false;
	$scope.file_type_alert = false;

    $scope.uploadFile = function () {

        var file = $scope.selectedFile[0];
        var photo = $scope.photo;
        var album_id = document.getElementById("photo-displayer").getAttribute('data-album-id');
		var user_id = document.getElementById("photo-displayer").getAttribute('data-user-id');

        $upload.upload({
            url: '/add_photo',
            method: 'POST',
            fields: {'photo_form': photo, 'album_id': album_id, 'user_id': user_id},
            file: file
		// }).progress(function (evt) {
			// $scope.uploadProgress = parseInt(100.0 * evt.loaded / evt.total, 10);
        }).success(function (data) {
			upload_result(data);
        });
    };

    function upload_result(data) {

		if (!data['pass_valid']) {

			console.log("Bad password!");
			$scope.password_alert = true;
			$scope.success_alert = false;
			$scope.file_type_alert = false;

		} else if (!data['valid_type']) {

			console.log("Wrong file type");
			$scope.file_type_alert = true;
			$scope.success_alert = false;
			$scope.password_alert = false;

		} else if (data['uploaded']) {

			console.log("Uploaded!");
			$rootScope.photos.push(data['photo_info']);
			$scope.success_alert = true;
			$scope.password_alert = false;
			$scope.file_type_alert = false;
			$scope.photo = {};
		}
    }

    $scope.onFileSelect = function ($files) {
        $scope.selectedFile = $files;
    };
}]);

// app.directive('progressBar', [
//     function () {
//         return {
//             link: function ($scope, el, attrs) {
//                 $scope.$watch(attrs.progressBar, function (newValue) {
//                     el.css('width', newValue.toString() + '%');
//                 });
//             }
//         };
//     }
// ]);


// jQuery
$(document).ready(function(){

	// toggles add album form on /albums
	$('#add-album-btn, #close-album-btn').on('click', function(){
		$('#add-album-form').slideToggle(200);
		$('#add-album-form').find("input[type=text], textarea").val("");
		$(this).children('i').toggleClass('fa-plus-circle fa-minus-circle');
	});

	// enable submit button on album form
	function enableSubmit() {
		$('#submit-album-btn').prop("disabled",false);
	}
	// doesn't let you submit album form if haven't selected owner
	$('#select-album-owner').on('change', enableSubmit);

	// add photo form hide/show toggle
	$('#add-photo-btn, #close-photo-btn').on('click', function() {
		$('#add-photo-form').slideToggle(200);
		$('#add-photo-form').find("input[type=text], textarea, input[type=file], input[type=password]").val("");
		$(this).children('i').toggleClass('fa-plus-circle fa-minus-circle');
	});

});

