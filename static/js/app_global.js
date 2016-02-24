(function() {

    $(function(){
        $('.alert:not(.dont-hide)').addClass('animated bounceIn');
        $(document).on('click', '.dialog-confirm', function(event) {
            bootbox.confirm($(this).data('title'), _.bind(function(result) {
                if (result) {
                    $(this).is(':button') ?
                        $(this).closest('form').submit() :
                        window.location.assign($(this).attr('href'));
                }
            }, this));

            event.preventDefault();
            return false;
        });
    });

    bootbox.setDefaults({
        animate: false
    });

})();
