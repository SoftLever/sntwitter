(function onBefore(current, previous /*null when async*/) {
    var text = current.comments.getJournalEntry(1);
    var target = current.u_twitter_user_id;
    try { 
        var r = new sn_ws.RESTMessageV2('Twitter DM', 'Send Message');
        r.setStringParameterNoEscape('user_id', 'your_user_id_here');
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
})(current, previous);