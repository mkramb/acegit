(function() {

    new (Backbone.View.extend({

        events: {
            'click :checkbox': 'select',
            'keyup #filter': 'filter'
        },

        initialize: function() {
            this.selected = [];
        },
        
        select: function(event) {
            var $element = $(event.target);
            var $button = this.$el.find(':submit');
             
            if ($element.is(':checked')) {
                this.selected.push($(event.target).val());
            }
            else {
                this.selected = _.without(
                    this.selected, $element.val()
                )
            }

            this.selected.length ? $button.removeAttr('disabled') :
                $button.attr('disabled', 'disabled');
        },
        
        filter: _.throttle(function(event) {
            var data = _.filter(
                $(event.target).val().replace(/\s+/g,' ').split(' ')
                ,Boolean
            );

            this.$el.find('.list-group-item').hide()
                .filter(function (i, v) {
                    var content = $(this).text().toLowerCase();

                    for (var i = 0; i < data.length; ++i) {
                        if (content.indexOf(data[i]) !== -1) {
                            return true;
                        }
                    }
                    
                    return !data.length;
                }).show()
        }, 500)

    }))({ el: $('#import') });

})();