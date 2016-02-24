(function() {

    $(function(){
        $(document).on('click', '#authenticate', function(event) {
            var form = $(this).closest('form');

            authenticate(function() {
                var token = Trello.token();               

                if (token && token.length) {
                    form.find(':input[name="_token"]')
                        .val(token).end().submit();
                }
            });
    
            event.preventDefault();
            return false;
        });
    });
    
    function authenticate(callback) {
        Trello.authorize({
            name: 'AceGit',
            type: 'popup',
            interactive: true,
            expiration: 'never',
            persist: false,
            success: callback,
            scope: {
                write: false,
                read: true
            }
        });
    }

})();