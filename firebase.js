// Import the functions you need from the Firebase SDK
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDvVAq-wPiZnMhawTFB-ElbFOELE0Mpn0s",
  authDomain: "sbirexnel.firebaseapp.com",
  projectId: "sbirexnel",
  storageBucket: "sbirexnel.firebasestorage.app",
  messagingSenderId: "32772427992",
  appId: "1:32772427992:web:deb4c4bc62f980764087ad",
  measurementId: "G-FST5VKSEMM"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };