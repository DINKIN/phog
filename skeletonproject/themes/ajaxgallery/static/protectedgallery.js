
function ProtectedGallery(promptDialogId,passwordBoxId) {
	this.promptDialogId=promptDialogId;
	this.passwordBoxId=passwordBoxId;
}

ProtectedGallery.prototype.passwordPrompt = function() {
	var pg=this;
	$("#"+this.promptDialogId).dialog({
		modal: true,
		title: 'Enter Password:',
		buttons: {
			"Submit": function() {
				var password=$("#"+pg.passwordBoxId).val();
				pg.tryPassword(password);
			}
		}
	});
}

ProtectedGallery.prototype.tryPassword = function(password) {
	// find all of the protected items on the page
	var protectedItems = $(".protectableitem");

	// hash the title and the password of the first one, see if it the resulting url is valid
	
	
	// if it isn't, show error

	// otherwise, go through and replace all of the urls.
	for (item in protectedItems) {


	}
	

}

