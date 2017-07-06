(function () {
    var timeoutId = null;
    var interval = 30000;

    var updatebuilds = function() {
        jQuery.ajax({
            url: jQuery("#runbuild form").attr('action'),
            method: "GET",
            data: {statuscheck: 1},
            success: function(data) {
                var tbody = jQuery('#buildstatus tbody');
                var rows = tbody.find('tr');
                if (rows.length > data.length) {
                    // need to truncate rows to match data (probably shouldn't ever happen but whatever)
                    rows.slice(data.length - rows.length).remove();
                }
                while (data.length > rows.length) {
                    // need to add rows to match data
                    (function (tbody, newindex) {
                        var newrow = jQuery('<tr>');
                        jQuery('#buildstatus thead tr th').each(function() {
                            newrow.append(jQuery('<td>').attr('class', this.className));
                        });
                        newrow.find('td.tableindex').html(newindex);
                        tbody.append(newrow);
                    })(tbody, rows.length + 1);
                    // update rows result
                    rows = tbody.find('tr');
                }
                rows.each(function() {
                    var nextrow = data.shift();
                    for (var field in nextrow) {
                        jQuery(this).find('td.'+field).html(nextrow[field]);
                    }
                    var indexfield = jQuery(this).find('td.tableindex');
                    var currentval = indexfield.html();
                    indexfield.html(
                        '<a href="'+window.location.pathname+'?buildid='+nextrow.id+'">'+currentval+'</a>'
                    );
                });
            }
        });
        timeoutId = setTimeout(updatebuilds, interval);
    };

    window.onload = function() {
        jQuery("#runbuild form").submit(function() {
            clearTimeout(timeoutId);
            jQuery.ajax({
                url: jQuery(this).attr('action'),
                method: "POST",
                data: jQuery(this).serialize(),
                dataType: "text",
                timeout: 500,
                complete: updatebuilds
            });
            return false;
        });

        timeoutId = setTimeout(updatebuilds, interval);
    };
})();
