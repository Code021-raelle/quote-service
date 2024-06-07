document.getElementById('review-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);

    fetch('/submit_review', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addReviewToDOM(formData);
            document.getElementById('review-form').reset();
        }
    });
});

function addReviewToDOM(formData) {
    const reviewsContainer = document.getElementById('reviews-container');
    const reviewDiv = document.createElement('div');
    reviewDiv.className = 'bg-white p-6 rounded-lg shadow-lg';
    
    const rating = parseFloat(formData.get('rating'));

    reviewDiv.innerHTML = `
        <div class="flex items-center mb-4">
            <img class="w-12 h-12 rounded-full object-cover" src="/static/uploads/${formData.get('avatar').name}" alt="${formData.get('name')}">
            <div class="ml-4">
                <h3 class="text-xl font-bold text-gray-900">${formData.get('name')}</h3>
                <p class="text-gray-600">${formData.get('job')}</p>
                <div class="flex items-center mt-2">
                    ${[...Array(5)].map((_, i) => {
                        if (i < rating) return '<i class="fas fa-star text-yellow-500"></i>';
                        if (i < rating + 0.5) return '<i class="fas fa-star-half-alt text-yellow-500"></i>';
                        return '<i class="far fa-star text-yellow-500"></i>';
                    }).join('')}
                </div>
            </div>
        </div>
        <p class="text-gray-700">${formData.get('review')}</p>
    `;
    reviewsContainer.appendChild(reviewDiv);
}