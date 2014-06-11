/**
 * Created by ante on 2014-03-28.
 */
$('document').ready(function(){
    $('.media-files').sortable();

    require(["/static/editor/javascript/mmSaveAndLoadRoute.js"],
        function(mmSaveAndLoadRoute) {
            $('.saveroutename').on('click',function(){
                mmSaveAndLoadRoute.saveRouteName();
            });
        });



});