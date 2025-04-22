// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-app.js";
import { 
  getAuth, 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword,
  onAuthStateChanged,
  signOut
} from "https://www.gstatic.com/firebasejs/10.11.1/firebase-auth.js";
import {
  getFirestore, 
  setDoc, 
  doc, 
  getDoc,
  updateDoc,
  onSnapshot
} from "https://www.gstatic.com/firebasejs/10.11.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyA4hm209AmrA0T8t0BE6kpZycXTqfCQSZE",
  authDomain: "sbiproto.firebaseapp.com",
  projectId: "sbiproto",
  storageBucket: "sbiproto.firebasestorage.app",
  messagingSenderId: "911630312572",
  appId: "1:911630312572:web:e9329e42c5d7db335395f9",
  measurementId: "G-FGTJW6LV5B"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// Function to show messages with fade effect
function showMessage(message, divId) {
  const messageDiv = document.getElementById(divId);
  if (!messageDiv) {
    console.error(`Message div with id ${divId} not found`);
    return;
  }
  
  messageDiv.style.display = "block";
  messageDiv.innerHTML = message;
  messageDiv.style.opacity = 1;
  
  setTimeout(function() {
    messageDiv.style.opacity = 0;
    setTimeout(function() {
      messageDiv.style.display = "none";
    }, 1000);
  }, 5000);
}

// Track our real-time listener so we can unsubscribe when needed
let userDataUnsubscribe = null;

// Setup real-time listener for user data
function setupUserDataListener(userId) {
  console.log("Setting up real-time listener for user:", userId);
  
  // Clear any existing listener first
  if (userDataUnsubscribe) {
    userDataUnsubscribe();
    userDataUnsubscribe = null;
  }

  if (!userId) {
    console.error("Cannot setup listener: No user ID provided");
    return;
  }

  const userDocRef = doc(db, "users", userId);
  
  // Set up real-time listener
  userDataUnsubscribe = onSnapshot(userDocRef, (docSnapshot) => {
    if (docSnapshot.exists()) {
      const userData = docSnapshot.data();
      console.log("Real-time update received:", userData);
      
      // Update UI with user data
      updateUserInterface(userData);
    } else {
      console.warn("User document does not exist in Firestore");
    }
  }, (error) => {
    console.error("Error in Firestore listener:", error);
  });
}

// Update the UI elements with user data
function updateUserInterface(userData) {
  // Update coin count
  const coinCountElement = document.getElementById('coin-count');
  if (coinCountElement) {
    coinCountElement.textContent = userData.coins || 0;
  } else {
    console.warn("Coin count element not found in DOM");
  }
  
  // Update badge display
  const badgeElement = document.getElementById('badge-name');
  if (badgeElement) {
    const badgeText = userData.badges && userData.badges.length > 0 
      ? userData.badges[0] 
      : "No Badge";
    badgeElement.textContent = badgeText;
  } else {
    console.warn("Badge element not found in DOM");
  }
}

// Add coins to user account
async function addUserCoins(userId, coinsToAdd) {
  if (!userId) {
    console.error("Cannot add coins: No user ID provided");
    return false;
  }

  try {
    const userDocRef = doc(db, "users", userId);
    const userDoc = await getDoc(userDocRef);
    
    if (userDoc.exists()) {
      const currentCoins = userDoc.data().coins || 0;
      const newCoins = currentCoins + coinsToAdd;
      
      await updateDoc(userDocRef, { coins: newCoins });
      console.log(`Added ${coinsToAdd} coins. New total: ${newCoins}`);
      return true;
    } else {
      console.error("User document not found in Firestore");
      return false;
    }
  } catch (error) {
    console.error("Error adding coins:", error);
    return false;
  }
}

// Add a badge to user account
async function addUserBadge(userId, badgeName) {
  if (!userId || !badgeName) {
    console.error("Cannot add badge: Missing user ID or badge name");
    return false;
  }

  try {
    const userDocRef = doc(db, "users", userId);
    const userDoc = await getDoc(userDocRef);
    
    if (userDoc.exists()) {
      const currentBadges = userDoc.data().badges || [];
      
      if (!currentBadges.includes(badgeName)) {
        const updatedBadges = [...currentBadges, badgeName];
        await updateDoc(userDocRef, { badges: updatedBadges });
        console.log(`Added badge: ${badgeName}`);
        return true;
      } else {
        console.log(`User already has badge: ${badgeName}`);
        return false;
      }
    } else {
      console.error("User document not found in Firestore");
      return false;
    }
  } catch (error) {
    console.error("Error adding badge:", error);
    return false;
  }
}

// Sign-up functionality
const signUpButton = document.getElementById('submitSignUp');
if (signUpButton) {
  signUpButton.addEventListener('click', async (event) => {
    event.preventDefault();
    
    const email = document.getElementById('rEmail')?.value;
    const password = document.getElementById('rPassword')?.value;
    const firstName = document.getElementById('fName')?.value;
    const lastName = document.getElementById('lName')?.value;
    
    if (!email || !password) {
      showMessage('Please fill all required fields', 'signUpMessage');
      return;
    }

    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      console.log("New user created:", user.uid);
      
      const userData = {
        email: email,
        firstName: firstName || '',
        lastName: lastName || '',
        coins: 1000,
        badges: ["Novice"]
      };
      
      await setDoc(doc(db, "users", user.uid), userData);
      showMessage('Account created successfully!', 'signUpMessage');
      
      // Redirect to login page
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 2000);
    } catch (error) {
      console.error("Error during sign up:", error);
      
      if (error.code === 'auth/email-already-in-use') {
        showMessage('Email address already exists!', 'signUpMessage');
      } else {
        showMessage(`Registration failed: ${error.message}`, 'signUpMessage');
      }
    }
  });
}

// Sign-in functionality
const signInButton = document.getElementById('submitSignIn');
if (signInButton) {
  signInButton.addEventListener('click', async (event) => {
    event.preventDefault();
    
    const email = document.getElementById('email')?.value;
    const password = document.getElementById('password')?.value;
    
    if (!email || !password) {
      showMessage('Please enter both email and password', 'signInMessage');
      return;
    }

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Store user ID in localStorage for persistence
      localStorage.setItem('loggedInUserId', user.uid);
      
      showMessage('Login successful!', 'signInMessage');
      
      // Redirect to home page
      setTimeout(() => {
        window.location.href = 'index.html';
      }, 1000);
    } catch (error) {
      console.error("Error during sign in:", error);
      
      if (error.code === 'auth/invalid-credential') {
        showMessage('Incorrect email or password', 'signInMessage');
      } else {
        showMessage(`Login failed: ${error.message}`, 'signInMessage');
      }
    }
  });
}

// Logout functionality
const logoutButton = document.getElementById('logout-item');
if (logoutButton) {
  logoutButton.addEventListener('click', async (event) => {
    event.preventDefault();
    
    try {
      await signOut(auth);
      localStorage.removeItem('loggedInUserId');
      
      // Clean up listener
      if (userDataUnsubscribe) {
        userDataUnsubscribe();
        userDataUnsubscribe = null;
      }
      
      // Redirect to login page
      window.location.href = 'login.html';
    } catch (error) {
      console.error("Error signing out:", error);
    }
  });
}

// Handle authentication state changes
onAuthStateChanged(auth, (user) => {
  const loginItem = document.getElementById('login-item');
  const logoutItem = document.getElementById('logout-item');
  
  if (user) {
    // User is signed in
    console.log("User is signed in:", user.uid);
    
    // Update UI visibility
    if (loginItem) loginItem.style.display = "none";
    if (logoutItem) logoutItem.style.display = "block";
    
    // Setup real-time listener
    setupUserDataListener(user.uid);
  } else {
    // User is signed out
    console.log("User is signed out");
    
    // Update UI visibility
    if (loginItem) loginItem.style.display = "block";
    if (logoutItem) logoutItem.style.display = "none";
    
    // Clean up listener
    if (userDataUnsubscribe) {
      userDataUnsubscribe();
      userDataUnsubscribe = null;
    }
  }
});

// Initialize on page load - check for stored user ID
document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM loaded - checking for stored user ID");
  
  // Get user ID from localStorage
  const userId = localStorage.getItem('loggedInUserId');
  
  if (userId) {
    console.log("Found stored user ID:", userId);
    setupUserDataListener(userId);
  } else {
    console.log("No stored user ID found");
  }
});

// Export functions for external use
window.addUserCoins = addUserCoins;
window.addUserBadge = addUserBadge;