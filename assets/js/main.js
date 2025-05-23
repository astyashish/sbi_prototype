






















/*=============== SHOW MENU ===============*/
const navMenu = document.getElementById('nav-menu'),
    navToggle = document.getElementById('nav-toggle'),
    navClose = document.getElementById('nav-close');

/*===== MENU SHOW =====*/
/* Validate if constant exists */
if (navToggle) {
    navToggle.addEventListener('click', () => {
        navMenu.classList.add('show-menu');
    })
}

/*===== MENU HIDDEN =====*/
/* Validate if constant exists */
if (navClose) {
    navClose.addEventListener('click', () => {
        navMenu.classList.remove('show-menu');
    })
}


/*=============== REMOVE MENU MOBILE ===============*/
const navLink = document.querySelectorAll('.nav__link')

function linkAction() {
    const navMenu = document.getElementById('nav-menu');
    // When we click on each nav__link, we remove the show-menu class
    navMenu.classList.remove('show-menu');
}
navLink.forEach(n => n.addEventListener('click', linkAction));

/*=============== CHANGE BACKGROUND HEADER ===============*/
function scrollHeader() {
    const header = document.getElementById('header')
    // When the scroll is greater than 50 viewport height, add the scroll-header class to the header tag
    if (this.scrollY >= 50) header.classList.add('scroll-header'); else header.classList.remove('scroll-header')
}
window.addEventListener('scroll', scrollHeader)

/*===============  JS FOR VIDEO SLIDER ===============*/
const btns = document.querySelectorAll(".slider__bg-navBtn");
const slides = document.querySelectorAll(".video__slide");

var sliderNav = function(manual){
    btns.forEach((btn) => {
        btn.classList.remove("active");
    });

    slides.forEach((slide) => {
        slide.classList.remove("active");
    });


    btns[manual].classList.add("active");
    slides[manual].classList.add("active");
}

btns.forEach((btn, i) =>{
    btn.addEventListener("click", () => {
        sliderNav(i);
    });
});


/*=============== POPULAR SWIPER ===============*/

let swiperPopular = new Swiper(".popular__container", {
    loop: true,
    spaceBetween: 24,
    slidesPerView: 'auto',
    grabCursor:true,


    pagination: {
      el: ".swiper-pagination",
      dynamicBullets: true,
    },

    breakpoints: {
        
        768: {
          slidesPerView: 3,

        },
        1024: {
          
          spaceBetween: 48,
        },
      },
});

/*=============== MIXITUP FILTER FEATURED ===============*/

let mixerFeatured = mixitup('.featured__content', {
    selectors: {
        target: '.featured__card'
    },
    animation: {
        duration: 300
    }
});

/* Link active color featured */

const linkFeatured = document.querySelectorAll('.featured__item');

function activeFeatured(){
    linkFeatured.forEach(l=>l.classList.remove('active-featured'));
    this.classList.add('active-featured');
}

linkFeatured.forEach(l=> l.addEventListener('click', activeFeatured));


/*=============== SHOW SCROLL UP ===============*/
function scrollUp(){
    const scrollUp = document.getElementById('scroll-up');
    // When the scroll is higher than 350 viewport height, add the show-scroll class to the a tag with the scroll-top class
    if(this.scrollY >= 350) scrollUp.classList.add('show-scroll'); else scrollUp.classList.remove('show-scroll')
}
window.addEventListener('scroll', scrollUp)

/*=============== SCROLL SECTIONS ACTIVE LINK ===============*/

const sections = document.querySelectorAll('section[id]')

function scrollActive(){
    const scrollY = window.pageYOffset

    sections.forEach(current =>{
        const sectionHeight = current.offsetHeight,
              sectionTop = current.offsetTop - 58,
              sectionId = current.getAttribute('id')

        if(scrollY > sectionTop && scrollY <= sectionTop + sectionHeight){
            document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.add('active-link')
        }else{
            document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.remove('active-link')
        }
    })
}
window.addEventListener('scroll', scrollActive)


const d = new Date();
document.getElementById("date").innerHTML = d;


/*=============== SCROLL REVEAL ANIMATION ===============*/

const sr = ScrollReveal({
    origin: 'top',
    distance: '60px',
    duration: 2500,
    delay: 400,
    //reset: true
})


sr.reveal(`.home__title, .popular__container, .features__img, .featured__filters`);
sr.reveal(`.home__subtitle`, {delay: 500});
sr.reveal(`.home__elec`, {delay: 600});
sr.reveal(`.home__img`, {delay: 800});
sr.reveal(`.home__car-data, .footer__copy`, {delay: 900, interval: 100, origin: 'bottom'});
sr.reveal(`.home__button`, {delay: 1000, origin: 'bottom'});

sr.reveal(`.about__group, .offer__data`, {origin: 'left'});
sr.reveal(`.about__data, .offer__img, .home__social-icon`, {origin: 'right'});

sr.reveal(`.features__map, .slider__bg`, {delay:600, origin: 'bottom'});
sr.reveal(`.features__card`, {interval: 300});
sr.reveal(`.featured__card, .logos__content, .footer__content`, {interval: 100});


// Function to fetch and parse the CSV file
async function fetchCSVAndUpdateCoins() {
    try {
      // Fetch the CSV file
      const response = await fetch('insurance_data_example.csv'); // Replace with the correct path to your CSV file
      const data = await response.text();
  
      // Parse the CSV data
      const rows = data.split('\n').slice(1); // Remove the header row
  
      // Find the user's coin count (assuming the first row is the current user)
      const userRow = rows[0]; // Use the first row as an example
      const columns = userRow.split(','); // Split the row into columns
      const coins = columns[columns.length - 1].trim(); // Extract the coins (last column)
  
      // Update the coin count in the menu bar
      const coinCountElement = document.getElementById('coin-count');
      if (coinCountElement) {
        coinCountElement.textContent = coins; // Update the coin count
      }
    } catch (error) {
      console.error('Error fetching or parsing CSV:', error);
    }
  }
  
  // Call the function to fetch and update the coin count
  fetchCSVAndUpdateCoins();
    

























  /*=============== LOGIN/LOGOUT FUNCTIONALITY ===============*/
const loginItem = document.getElementById('login-item');
const logoutItem = document.getElementById('logout-item');
const logoutLink = document.getElementById('logout-link');
const coincount = document.getElementById('coin-link')

// Function to update auth UI
function updateAuthUI(user) {
    if (user) {
        // User is logged in
        if (loginItem) loginItem.style.display = 'none';
        if (logoutItem) logoutItem.style.display = 'block';
        if (coincount) coincount.style.display='block';
    } else {
        // User is logged out
        if (loginItem) loginItem.style.display = 'block';
        if (logoutItem) logoutItem.style.display = 'none';
        if (coincount) coincount.style.display = 'none';
    }
}

// Initialize auth state from localStorage
function checkAuthState() {
    const loggedInUserId = localStorage.getItem('loggedInUserId');
    updateAuthUI(loggedInUserId ? { uid: loggedInUserId } : null);
}

// Logout functionality
if (logoutLink) {
    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('loggedInUserId');
        updateAuthUI(null);
        window.location.href = 'index.html';
    });
}

// Check auth state when page loads
document.addEventListener('DOMContentLoaded', checkAuthState);

// Close mobile menu when clicking login/logout
if (loginItem) {
    loginItem.addEventListener('click', () => {
        document.getElementById('nav-menu').classList.remove('show-menu');
    });
}

if (logoutLink) {
    logoutLink.addEventListener('click', () => {
        document.getElementById('nav-menu').classList.remove('show-menu');
    });
}