
$(document).ready(function() {
	$('#nextBtn').click(function() {
		$.get('/next', function(data) {
			$('#quote').text(data.quote);
		});
	});

	$('#prevBtn').click(function() {
		$.get('/prev', function(data) {
			$('#quote').text(data.quote);
		});
	});
});
