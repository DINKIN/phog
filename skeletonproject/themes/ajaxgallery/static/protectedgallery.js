
function ProtectedGallery(promptDialogId) {
	this.promptDialogId=promptDialogId;
}

ProtectedGallery.prototype.passwordPrompt = function() {
	$(this.promptDialogId).dialog({
		autoOpen: false,
		modal: true,
		buttons: {
			"Enter": function() {
				alert("pressed enter");
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


}

