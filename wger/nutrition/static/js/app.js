var app = angular.module('plunker', []);

app.controller('MainCtrl', function($scope) {
  $scope.receivers=[{hour:"", mealItems:[{content:"" , quantity:"", weightUnit:"g"}]}];

  $scope.addRecipient = function(receiver) {
    $scope.receivers.push({hour:"", mealItems:[{content:"" , quantity:"", weightUnit:"g"}]});
  }

  $scope.deleteRecipient = function(receiver) {
    for(var i=0; i<$scope.receivers.length; i++) {
      if($scope.receivers[i] === receiver) {
        $scope.receivers.splice(i, 1);
        break;
      }
    }
    if ($scope.receivers.length == 0){
		$scope.addRecipient();
	}
  }
  
    $scope.addIngredient = function(Items) {
		Items.push({content:"" , quantity:"", weightUnit:"g"});
  }

  $scope.deleteIngredient = function(receiver, Ingredient) {
     for(var j=0; j<receiver.mealItems.length; j++){
		if(receiver.mealItems[j] === Ingredient){
			receiver.mealItems.splice(j, 1);
			break;
		}
      }
    if (receiver.mealItems.length == 0){
		addIngredient(receiver.mealItems);
	}
  }

  $scope.showme = function() {
    var s = "";
    for(var i=0; i<$scope.receivers.length; i++) {
      s = s + i + ": " + $scope.receivers[i].hour + " " + $scope.receivers[i].content + "\n";
    }
    alert(s);
  };
  

});
