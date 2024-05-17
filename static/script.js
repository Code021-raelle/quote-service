
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

// Add event listeners for keydown events
document.addEventListener('keydown', function(event) {
	if (event.key === 'ArrowRight') {
		document.getElementById('nextBtn').click();
	} else if (event.key === 'ArrowLeft') {
		document.getElementById('prevBtn').click();
	}
});

