$('document').ready(function(){
    require(["/static/editor/javascript/mmEditor.js","/static/editor/javascript/mmSaveAndLoadRoute.js"],
        function(mmEditor,mmSaveAndLoadRoute) {
            mmEditor.initializeEditor(mmSaveAndLoadRoute);

            $(window).on('beforeunload', function() {
                if(!mmEditor.isSaved()){
                    return "Du har osparade ändringar, säker du vill lämna sidan?";
                }
            }); 
            
            var data = mmSaveAndLoadRoute.getEditorData(mmEditor.loadRoute)
            
            
            $('.station').on('click',function(){
                mmEditor.addStation();
            });
            $('.saveRoute').on('click',function(){
                mmEditor.saveEditor();
                mmSaveAndLoadRoute.saveToDatabase(mmEditor.getStations(),mmEditor.getPath());
            });

        });
});

