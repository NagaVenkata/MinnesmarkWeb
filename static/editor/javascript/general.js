/**
 * Created by ante on 2014-03-28.
 */
$('document').ready(function(){
    
    
    $('.media-files').sortable();
});

function saveName() {
    require(["/static/editor/javascript/mmSaveAndLoadRoute.js"],
	    function(mmSaveAndLoadRoute) {
                mmSaveAndLoadRoute.saveRouteName();
	    });
}

