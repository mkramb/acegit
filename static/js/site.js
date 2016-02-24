(function() {

    $(function(){
        $(document).on('click', '#sign-in', function(event) {
            var $element = $(this);

            if (!$element.data('disabled')) {
                $element.find('i')
                    .removeClass('fa-github fa-lg')
                    .addClass('fa-circle-o-notch fa-spin')
                    .end().data('disabled', true);

                _.delay(_.bind(function() {
                    window.location.assign($(this).attr('href'));
                }, this), 500);
            }

            event.preventDefault();
            return false;
        });
    });

})();
