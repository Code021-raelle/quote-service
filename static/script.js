
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

let currentFontStyle = 0;
const fontStyles = ['font-style-1', 'font-style-2', 'font-style-3'];

document.getElementById('fontToggle').addEventListener('click', () => {
	const quoteContainer = document.getElementById('quoteContainer');
	quoteContainer.classList.remove(...fontStyles);
	currentFontStyle = (currentFontStyle + 1) % fontStyle.length;
	quoteContainer.classList.add(fontStyle[currentFontStyle]);
});

