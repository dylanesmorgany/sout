// Basic carousel for testimonials
const reviews = document.querySelectorAll('.review');
let current = 0;
setInterval(() => {
  reviews[current].style.display = 'none';
  current = (current + 1) % reviews.length;
  reviews[current].style.display = 'block';
}, 3000);
