(function onBefore(current, previous /*null when async*/) {
    var text = current.comments.getJournalEntry(1);
    var target = current.opened_by;
	if (gs.isInteractive()) { // This will not execute for changes coming from API -> This way, we'll avoid infinite exchange of the same texts
		try { 
			var r = new sn_ws.RESTMessageV2('Twitter DM', 'Send Message');
			r.setStringParameterNoEscape('target', target);
			r.setStringParameterNoEscape('message', text);

			var response = r.executeAsync();
			response.waitForResponse(10);
			var responseBody = response.getBody();
			var httpStatus = response.getStatusCode();
		}
		catch(ex) {
			var message = ex.message;
			gs.addInfoMessage(message);
		}
	}
})(current, previous);