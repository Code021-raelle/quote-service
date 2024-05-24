document.addEventListener("DOMContentLoaded", () => {
    const reviewForm = document.getElementById("review-form");
    const reviewsContainer = document.getElementById("reviews-container");
    const defaultAvatar = 'https://via.placeholder.com/48'; // default avatar if none provided

    // Load existing reviews from localStorage
    loadReviews();

    reviewForm.addEventListener("submit", function(event) {
        event.preventDefault();

        const name = document.getElementById("name").value;
        const job = document.getElementById("job").value;
        const avatarFile = document.getElementById("avatar").files[0];
        const rating = parseFloat(document.getElementById("rating").value);
        const reviewText = document.getElementById("review").value;

        const reader = new FileReader();

        reader.onload = function(event) {
            const avatarUrl = event.target.result || defaultAvatar;

            const review = {
                name,
                job,
                avatarUrl,
                rating,
                reviewText
            };

            // Add review to DOM
            addReviewToDOM(review);

            // Save review to localStorage
            saveReview(review);

            reviewForm.reset();
        };

        if (avatarFile) {
            reader.readAsDataURL(avatarFile);
        } else {
            reader.onload({ target: { result: defaultAvatar } });
        }
    });

    function getStarRatingHTML(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 !== 0 ? 1 : 0;

        let starsHTML = '';
        for (let i = 0; i < fullStars; i++) {
            starsHTML += '<i class="fas fa-star text-yellow-500"></i>';
        }

        if (halfStar) {
            starsHTML += '<i class="fas fa-star-half-alt text-yellow-500"></i>';
        }

        for (let i = fullStars + halfStar; i < 5; i++) {
            starsHTML += '<i class="far fa-star text-yellow-500"></i>';
        }

        return starsHTML;
    }

    function addReviewToDOM(review) {
        const reviewElement = document.createElement("div");
        reviewElement.classList.add("bg-white", "p-6", "rounded-lg", "shadow-lg");

        const stars = getStarRatingHTML(review.rating);

        reviewElement.innerHTML = `
            <div class="flex items-center mb-4">
                <img class="w-12 h-12 rounded-full object-cover" src="${review.avatarUrl}" alt="${review.name}">
                <div class="ml-4">
                    <h3 class="text-xl font-bold text-gray-900">${review.name}</h3>
                    <p class="text-gray-600">${review.job}</p>
                    <div class="flex items-center mt-2">${stars}</div>
                </div>
            </div>
            <p class="text-gray-700">${review.reviewText}</p>
        `;

        reviewsContainer.appendChild(reviewElement);
    }

    function saveReview(review) {
        let reviews = JSON.parse(localStorage.getItem("reviews")) || [];
        reviews.push(review);
        localStorage.setItem("reviews", JSON.stringify(reviews));
    }

    function loadReviews() {
        const reviews = JSON.parse(localStorage.getItem("reviews")) || [];
        reviews.forEach(review => {
            addReviewToDOM(review);
        });
    }
});

