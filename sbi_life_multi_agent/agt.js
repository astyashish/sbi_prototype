// Insurance policy data (same as in Python code)
const POLICIES = {
  "sbipp1": {
      "name": "SBI Life - Shield Plus",
      "type": "Protection",
      "description": "Term life insurance with high coverage",
      "premium": "₹10,000/year",
      "coverage": "₹1 Crore",
      "duration": "10-30 years",
      "features": ["High death benefit", "Affordable premiums", "Flexible terms"]
  },
  "sbipp2": {
      "name": "SBI Life - Smart Protection",
      "type": "Protection",
      "description": "Term plan with return of premium",
      "premium": "₹15,000/year",
      "coverage": "₹75 Lakhs",
      "duration": "15-25 years",
      "features": ["Premium return", "Critical illness cover", "Tax benefits"]
  },
  "sbisp1": {
      "name": "SBI Life - Savings Plus",
      "type": "Savings",
      "description": "Endowment plan with guaranteed returns",
      "premium": "₹50,000/year",
      "coverage": "₹10 Lakhs",
      "duration": "10-20 years",
      "features": ["Guaranteed returns", "Bonus additions", "Loan facility"]
  },
  "sbirp1": {
      "name": "SBI Life - Retirement Plus",
      "type": "Retirement",
      "description": "Pension plan with life cover",
      "premium": "₹60,000/year",
      "coverage": "₹15 Lakhs",
      "duration": "Till retirement",
      "features": ["Regular pension", "Life cover", "Tax-free maturity"]
  },
  "sbicp1": {
      "name": "SBI Life - Child Plan",
      "type": "Child",
      "description": "Education savings with insurance cover",
      "premium": "₹20,000/year",
      "coverage": "₹5 Lakhs",
      "duration": "10-15 years",
      "features": ["Education fund", "Waiver of premium", "Flexible payout options"]
  }
};

// Compute categories dynamically (same as Python code)
const CATEGORIES = [...new Set(Object.values(POLICIES).map(p => p.type))];
const PLANS_BY_CATEGORY = {};
CATEGORIES.forEach(category => {
  PLANS_BY_CATEGORY[category] = Object.keys(POLICIES).filter(
      pid => POLICIES[pid].type === category
  );
});

// User data object
const userData = {
  user_id: "user_" + Math.floor(Math.random() * 100000),
  clicks: {},
  personal_info: {},
  preferences: {},
  interaction_history: [],
  recommendations: []
};

// Initialize clicks data structure
CATEGORIES.forEach(category => {
  userData.clicks[category] = {};
  PLANS_BY_CATEGORY[category].forEach(plan => {
      userData.clicks[category][plan] = 0;
  });
});

// DOM elements
const sections = document.querySelectorAll('.section');
const steps = document.querySelectorAll('.step');
const loadingSection = document.getElementById('loading-section');
const apiErrorSection = document.getElementById('api-error');

// Navigation buttons
const next1Button = document.getElementById('next1');
const next2Button = document.getElementById('next2');
const next3Button = document.getElementById('next3');
const prev2Button = document.getElementById('prev2');
const prev3Button = document.getElementById('prev3');
const prev4Button = document.getElementById('prev4');
const restartButton = document.getElementById('restart');
const retryButton = document.getElementById('retry-btn');

// Generate browsing behavior cards
function generateBrowsingCards() {
  const container = document.getElementById('browsing-behavior-container');
  container.innerHTML = '';
  
  CATEGORIES.forEach(category => {
      const categoryTitle = document.createElement('h3');
      categoryTitle.textContent = category + ' Policies';
      categoryTitle.style.marginTop = '20px';
      categoryTitle.style.marginBottom = '10px';
      container.appendChild(categoryTitle);
      
      PLANS_BY_CATEGORY[category].forEach(policyId => {
          const policy = POLICIES[policyId];
          
          const card = document.createElement('div');
          card.className = 'policy-card';
          
          const info = document.createElement('div');
          info.className = 'policy-info';
          
          const name = document.createElement('div');
          name.className = 'policy-name';
          name.textContent = policy.name;
          
          const type = document.createElement('div');
          type.className = 'policy-type';
          type.textContent = policy.type;
          
          const description = document.createElement('div');
          description.className = 'policy-description';
          description.textContent = policy.description;
          
          const details = document.createElement('div');
          details.className = 'policy-details';
          
          const premium = document.createElement('div');
          premium.className = 'policy-detail';
          premium.textContent = `Premium: ${policy.premium}`;
          
          const coverage = document.createElement('div');
          coverage.className = 'policy-detail';
          coverage.textContent = `Coverage: ${policy.coverage}`;
          
          details.appendChild(premium);
          details.appendChild(coverage);
          
          info.appendChild(name);
          info.appendChild(type);
          info.appendChild(description);
          info.appendChild(details);
          
          const clicks = document.createElement('div');
          clicks.className = 'policy-clicks';
          
          const controlsLabel = document.createElement('label');
          controlsLabel.textContent = 'Views: ';
          
          const controls = document.createElement('div');
          controls.className = 'clicks-control';
          
          const minusBtn = document.createElement('div');
          minusBtn.className = 'clicks-btn';
          minusBtn.textContent = '-';
          minusBtn.onclick = () => adjustClicks(category, policyId, -1);
          
          const value = document.createElement('div');
          value.className = 'clicks-value';
          value.textContent = userData.clicks[category][policyId];
          value.id = `clicks-${policyId}`;
          
          const plusBtn = document.createElement('div');
          plusBtn.className = 'clicks-btn';
          plusBtn.textContent = '+';
          plusBtn.onclick = () => adjustClicks(category, policyId, 1);
          
          controls.appendChild(minusBtn);
          controls.appendChild(value);
          controls.appendChild(plusBtn);
          
          clicks.appendChild(controlsLabel);
          clicks.appendChild(controls);
          
          card.appendChild(info);
          card.appendChild(clicks);
          
          container.appendChild(card);
      });
  });
}

// Adjust clicks for a policy
function adjustClicks(category, policyId, delta) {
  const currentClicks = userData.clicks[category][policyId];
  const newClicks = Math.max(0, Math.min(10, currentClicks + delta));
  
  userData.clicks[category][policyId] = newClicks;
  document.getElementById(`clicks-${policyId}`).textContent = newClicks;
  
  // Log interaction
  logInteraction(`Adjusted ${policyId} views to ${newClicks}`);
}

// Log interaction
function logInteraction(description) {
  userData.interaction_history.push({
      timestamp: new Date().toISOString(),
      description: description
  });
}

// Navigate to a section
function navigateToSection(sectionIndex) {
  sections.forEach((section, index) => {
      section.classList.remove('active');
      steps[index].classList.remove('active', 'completed');
      
      if (index < sectionIndex - 1) {
          steps[index].classList.add('completed');
      } else if (index === sectionIndex - 1) {
          steps[index].classList.add('active');
      }
  });
  
  sections[sectionIndex - 1].classList.add('active');
}

// Collect user information
function collectUserInfo() {
  userData.personal_info = {
      age: parseInt(document.getElementById('age').value),
      income: document.getElementById('income').value,
      marital_status: document.getElementById('marital-status').value,
      dependents: parseInt(document.getElementById('dependents').value),
      financial_goals: document.getElementById('financial-goals').value
          .split(',').map(goal => goal.trim())
  };
  
  logInteraction("Updated personal information");
}

// Collect user preferences
function collectUserPreferences() {
  userData.preferences = {
      risk_appetite: document.getElementById('risk-appetite').value,
      preferred_term: document.getElementById('preferred-term').value,
      priority: document.getElementById('priority').value
  };
  
  logInteraction("Updated preferences");
}

// Analyze user data locally (implementing the Python algorithm in JavaScript)
function analyzeUserData() {
  const policyScores = {};
  
  // Calculate scores for policies based on user profile
  for (const policyId in POLICIES) {
      const policy = POLICIES[policyId];
      let score = 0;
      
      // Add click score (user interest)
      const category = policy.type;
      const clicks = userData.clicks[category]?.[policyId] || 0;
      score += clicks * 10;
      
      // Age-based scoring
      const age = userData.personal_info.age || 30;
      if (policy.type === 'Protection' && age < 35) {
          score += 30;
      } else if (policy.type === 'Child' && userData.personal_info.dependents > 0) {
          score += 30 * userData.personal_info.dependents;
      } else if (policy.type === 'Retirement' && age > 30) {
          score += (age - 30) * 2;  // Increases with age
      } else if (policy.type === 'Savings') {
          const goals = userData.personal_info.financial_goals || [];
          if (goals.some(goal => 
              ['house', 'home', 'car', 'education'].includes(goal.toLowerCase()))) {
              score += 25;
          }
      }
      
      // Priority alignment
      if (policy.type === userData.preferences.priority) {
          score += 40;
      }
      
      // Risk appetite alignment
      const riskAppetite = userData.preferences.risk_appetite || 'Medium';
      if (riskAppetite === 'Low' && policy.type === 'Protection') {
          score += 20;
      } else if (riskAppetite === 'Medium' && policy.type === 'Savings') {
          score += 20;
      } else if (riskAppetite === 'High' && policy.type === 'Retirement') {
          score += 20;
      }
      
      // Term preference alignment
      const preferredTerm = userData.preferences.preferred_term || 'Medium';
      const duration = policy.duration || '';
      
      if (preferredTerm === 'Short' && duration.includes('10')) {
          score += 15;
      } else if (preferredTerm === 'Medium' && 
                (duration.includes('15') || duration.includes('20'))) {
          score += 15;
      } else if (preferredTerm === 'Long' && 
                (duration.includes('25') || duration.includes('30'))) {
          score += 15;
      }
      
      policyScores[policyId] = score;
  }
  
  // Sort policies by score
  const sortedPolicies = Object.entries(policyScores).sort((a, b) => b[1] - a[1]);
  const topPolicies = sortedPolicies.slice(0, 3);
  
  // Generate analysis text
  const analysis = generateAnalysisText(topPolicies);
  
  return {
      analysis: analysis,
      recommended_policy_ids: topPolicies.map(p => p[0]),
      scores: Object.fromEntries(topPolicies)
  };
}

// Generate analysis text
function generateAnalysisText(topPolicies) {
  const age = userData.personal_info.age || 0;
  const income = userData.personal_info.income || '';
  const dependents = userData.personal_info.dependents || 0;
  const riskAppetite = userData.preferences.risk_appetite || 'Medium';
  
  let analysis = `## User Profile Analysis\n\n`;
  analysis += `Based on your profile as a ${age}-year-old with `;
  analysis += `${dependents} dependents and a ${riskAppetite.toLowerCase()} risk appetite, `;
  
  // Add needs analysis
  analysis += "we've identified these key insurance needs:\n\n";
  
  if (age < 30) {
      analysis += "- Early career stage: Focus on building financial security with basic protection\n";
  } else if (30 <= age < 45) {
      analysis += "- Mid-career stage: Balance between protection and long-term savings\n";
  } else {
      analysis += "- Late career stage: Focus on retirement planning and wealth preservation\n";
  }
  
  if (dependents > 0) {
      analysis += `- Family protection: Coverage needs for ${dependents} dependents\n`;
      if (userData.personal_info.financial_goals.some(
          d => d.toLowerCase().includes('education'))) {
          analysis += "- Education planning: Funding needs for children's education\n";
      }
  }
  
  // Add recommendation rationale
  analysis += "\n## Recommendation Rationale\n\n";
  for (const [pid, score] of topPolicies) {
      const policy = POLICIES[pid];
      analysis += `### ${policy.name}\n`;
      analysis += `- Type: ${policy.type}\n`;
      analysis += `- Recommendation score: ${score}\n`;
      analysis += `- Key benefits: ${policy.features.join(', ')}\n`;
      analysis += `- Suitability: `;
      
      // Add custom suitability text based on policy type
      if (policy.type === 'Protection') {
          analysis += "Provides essential financial security for you and your dependents\n";
      } else if (policy.type === 'Child') {
          analysis += "Secures your child's future education and financial needs\n";
      } else if (policy.type === 'Retirement') {
          analysis += "Builds your retirement corpus for financial independence\n";
      } else if (policy.type === 'Savings') {
          analysis += "Helps achieve your financial goals with guaranteed returns\n";
      } else {
          analysis += "Meets your specific insurance needs as identified\n";
      }
      
      analysis += "\n";
  }
  
  return analysis;
}

// Display recommendations
function displayRecommendations(result) {
  const container = document.getElementById('recommendations-container');
  container.innerHTML = '';
  
  result.recommended_policy_ids.forEach(policyId => {
      const policy = POLICIES[policyId];
      const score = result.scores[policyId];
      
      const card = document.createElement('div');
      card.className = 'recommendation-card';
      
      const title = document.createElement('h3');
      title.className = 'recommendation-title';
      title.textContent = policy.name;
      
      const subtitle = document.createElement('div');
      subtitle.className = 'recommendation-subtitle';
      subtitle.textContent = `${policy.type} | Score: ${score}`;
      
      const description = document.createElement('p');
      description.textContent = policy.description;
      
      const details = document.createElement('div');
      details.className = 'policy-details';
      
      const premium = document.createElement('div');
      premium.className = 'policy-detail';
      premium.textContent = `Premium: ${policy.premium}`;
      
      const coverage = document.createElement('div');
      coverage.className = 'policy-detail';
      coverage.textContent = `Coverage: ${policy.coverage}`;
      
      const duration = document.createElement('div');
      duration.className = 'policy-detail';
      duration.textContent = `Duration: ${policy.duration}`;
      
      details.appendChild(premium);
      details.appendChild(coverage);
      details.appendChild(duration);
      
      const featuresTitle = document.createElement('h4');
      featuresTitle.textContent = 'Key Features:';
      
      const features = document.createElement('div');
      features.className = 'recommendation-features';
      
      policy.features.forEach(feature => {
          const featureItem = document.createElement('div');
          featureItem.className = 'feature-item';
          featureItem.textContent = feature;
          features.appendChild(featureItem);
      });
      
      card.appendChild(title);
      card.appendChild(subtitle);
      card.appendChild(description);
      card.appendChild(details);
      card.appendChild(featuresTitle);
      card.appendChild(features);
      
      container.appendChild(card);
  });
  
  // Display analysis
  document.getElementById('analysis-content').textContent = result.analysis;
}

// Event listeners
next1Button.addEventListener('click', () => {
  navigateToSection(2);
});

next2Button.addEventListener('click', () => {
  collectUserInfo();
  navigateToSection(3);
});

next3Button.addEventListener('click', () => {
  collectUserPreferences();
  
  // Show loading section
  sections.forEach(s => s.classList.remove('active'));
  loadingSection.style.display = 'block';
  
  // Simulate processing delay
  setTimeout(() => {
      // Analyze user data
      const result = analyzeUserData();
      userData.recommendations.push(result);
      
      // Hide loading section
      loadingSection.style.display = 'none';
      
      // Display recommendations
      displayRecommendations(result);
      navigateToSection(4);
  }, 1500);
});

prev2Button.addEventListener('click', () => {
  navigateToSection(1);
});

prev3Button.addEventListener('click', () => {
  navigateToSection(2);
});

prev4Button.addEventListener('click', () => {
  navigateToSection(3);
});

restartButton.addEventListener('click', () => {
  // Reset user data
  CATEGORIES.forEach(category => {
      PLANS_BY_CATEGORY[category].forEach(plan => {
          userData.clicks[category][plan] = 0;
      });
  });
  
  // Reset form fields
  document.getElementById('age').value = '30';
  document.getElementById('income').value = '5-10L';
  document.getElementById('marital-status').value = 'Single';
  document.getElementById('dependents').value = '0';
  document.getElementById('financial-goals').value = 'retirement, house';
  document.getElementById('risk-appetite').value = 'Medium';
  document.getElementById('preferred-term').value = 'Medium';
  document.getElementById('priority').value = 'Protection';
  
  // Clear recommendations
  document.getElementById('recommendations-container').innerHTML = '';
  document.getElementById('analysis-content').textContent = '';
  
  // Regenerate browsing cards
  generateBrowsingCards();
  
  // Go back to first section
  navigateToSection(1);
});

retryButton.addEventListener('click', () => {
  apiErrorSection.style.display = 'none';
  next3Button.click();
});

// Initialize the app
generateBrowsingCards();