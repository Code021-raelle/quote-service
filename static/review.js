document.getElementById('review-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const review = {
        name: formData.get('name'),
        job: formData.get('job'),
        avatar: formData.get('avatar').name,
        rating: parseFloat(formData.get('rating')),
        review: formData.get('review')
    };

    fetch('/submit_review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(review)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addReviewToDOM(review);
            document.getElementById('review-form').reset();
        }
    });
});
