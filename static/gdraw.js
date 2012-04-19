
function process_latex() {
    $('pre.latex').each(function(e) {
      var tex = $(this).text();
      var url = "http://chart.apis.google.com/chart?cht=tx&chl=" + encodeURIComponent(tex);
      var cls = $(this).attr('class');
      var img = '<img src="' + url + '" alt="' + tex + '" class="' + cls + '"/>';
      $(img).css('display', 'block').insertBefore($(this));
      $(this).hide();
    });
  }

$(document).ready(function() {process_latex();});

	