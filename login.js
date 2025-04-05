// Import Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-auth.js";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDvVAq-wPiZnMhawTFB-ElbFOELE0Mpn0s",
  authDomain: "sbirexnel.firebaseapp.com",
  projectId: "sbirexnel",
  storageBucket: "sbirexnel.appspot.com",
  messagingSenderId: "32772427992",
  appId: "1:32772427992:web:deb4c4bc62f980764087ad",
  measurementId: "G-FST5VKSEMM"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth();

// Login form submission
const loginForm = document.getElementById('login-form');
const errorMessage = document.getElementById('error-message');

loginForm.addEventListener('submit', (e) => {
  e.preventDefault(); // Prevent form submission

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  // Sign in with email and password
  signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      // Redirect to the main website after successful login
      window.location.href = 'index.html';
    })
    .catch((error) => {
      // Display error message
      errorMessage.textContent = error.message;
      errorMessage.style.display = 'block';
    });
});