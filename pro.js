document.addEventListener('DOMContentLoaded', function() {
  // Sample product data
  const products = [
      { 
          id: "sbipp1", 
          name: "SBI Life – eShield Next", 
          price: "Varies based on coverage", 
          category: "Protection Plans", 
          description: "A term plan offering multiple coverage options, including increasing cover and level cover with future-proofing benefits." 
      },
      { 
          id: "sbipp2", 
          name: "SBI Life – Saral Jeevan Bima", 
          price: "Affordable premiums", 
          category: "Protection Plans", 
          description: "A straightforward term insurance plan ensuring financial protection at affordable premiums." 
      },
      { 
          id: "sbipp3", 
          name: "SBI Life – Sampoorna Cancer Suraksha", 
          price: "Varies based on coverage", 
          category: "Protection Plans", 
          description: "A specialized plan providing financial support upon cancer diagnosis." 
      },
      { 
          id: "sbisp1", 
          name: "SBI Life – Smart Swadhan Plus", 
          price: "Varies based on term", 
          category: "Savings Plans", 
          description: "A non-linked, non-participating term assurance plan with a return of premiums at maturity." 
      },
      { 
          id: "sbisp2", 
          name: "SBI Life – Shubh Nivesh", 
          price: "Varies based on coverage", 
          category: "Savings Plans", 
          description: "An endowment plan offering options for regular income and whole life coverage." 
      },
      { 
          id: "sbisp3", 
          name: "SBI Life – Smart Future Choices", 
          price: "Varies based on term", 
          category: "Savings Plans", 
          description: "A savings plan providing benefits on death, maturity, and survival, along with cash bonuses." 
      },
      { 
          id: "sbiu1", 
          name: "SBI Life – Smart Wealth Assure", 
          price: "Single premium", 
          category: "ULIPs", 
          description: "A single premium ULIP providing market-linked returns with life insurance coverage." 
      },
      { 
          id: "sbiu2", 
          name: "SBI Life – Smart Elite", 
          price: "High premium", 
          category: "ULIPs", 
          description: "A limited premium payment ULIP designed for high net-worth individuals." 
      },
      { 
          id: "sbirp1", 
          name: "SBI Life – Retire Smart", 
          price: "Varies based on term", 
          category: "Retirement Plans", 
          description: "A non-participating ULIP offering assured additions and terminal additions to boost your retirement corpus." 
      },
      { 
          id: "sbirp2", 
          name: "SBI Life – Saral Pension", 
          price: "Varies based on term", 
          category: "Retirement Plans", 
          description: "A traditional, participating pension plan providing a regular income after retirement." 
      }
  ];

  // List of recommended product IDs (using strings, not variables)
  const recommendedIds = ["sbipp1", "sbirp2", "sbiu1"];

  // DOM elements
  const productList = document.getElementById('product-list');
  const filterIdInput = document.getElementById('filter-id');
  const filterBtn = document.getElementById('filter-btn');
  const resetBtn = document.getElementById('reset-btn');
  const recommendedBtn = document.getElementById('recommended-btn');
  const sortBySelect = document.getElementById('sort-by');

  // Current filtered products (initially all products)
  let currentProducts = [...products];

  // Display products
  function displayProducts(productsToDisplay) {
      productList.innerHTML = '';
      
      if (productsToDisplay.length === 0) {
          productList.innerHTML = '<p class="no-products">No products found matching your criteria.</p>';
          return;
      }
      
      productsToDisplay.forEach(product => {
          const productCard = document.createElement('div');
          productCard.className = 'product-card';
          productCard.innerHTML = `
              <div class="product-id">ID: ${product.id}</div>
              <div class="product-name">${product.name}</div>
              <div class="product-price">${product.price}</div>
              <div class="product-category">${product.category}</div>
              <div class="product-description">${product.description}</div>
          `;
          productList.appendChild(productCard);
      });
  }

  // Filter products by ID
  function filterProductsById(id) {
      if (!id) return products;
      return products.filter(product => 
          product.id.toLowerCase().includes(id.toLowerCase())
      );
  }

  // Filter products to only show recommended ones
  function showRecommendedProducts() {
      return products.filter(product => 
          recommendedIds.includes(product.id)
      );
  }

  // Sort products
  function sortProducts(productsToSort, sortOption) {
      const sortedProducts = [...productsToSort];
      
      switch (sortOption) {
          case 'id-asc': 
              return sortedProducts.sort((a, b) => a.id.localeCompare(b.id));
          case 'id-desc': 
              return sortedProducts.sort((a, b) => b.id.localeCompare(a.id));
          case 'name-asc': 
              return sortedProducts.sort((a, b) => a.name.localeCompare(b.name));
          case 'name-desc': 
              return sortedProducts.sort((a, b) => b.name.localeCompare(a.name));
          case 'category-asc': 
              return sortedProducts.sort((a, b) => a.category.localeCompare(b.category));
          case 'category-desc': 
              return sortedProducts.sort((a, b) => b.category.localeCompare(a.category));
          default: 
              return sortedProducts;
      }
  }

  // Update product display based on current filters/sort
  function updateProductDisplay() {
      const sortValue = sortBySelect.value;
      const sortedProducts = sortProducts(currentProducts, sortValue);
      displayProducts(sortedProducts);
  }

  // Event listeners
  filterBtn.addEventListener('click', function() {
      const filterValue = filterIdInput.value.trim();
      currentProducts = filterProductsById(filterValue);
      updateProductDisplay();
  });

  resetBtn.addEventListener('click', function() {
      filterIdInput.value = '';
      currentProducts = [...products];
      updateProductDisplay();
  });

  recommendedBtn.addEventListener('click', function() {
      currentProducts = showRecommendedProducts();
      updateProductDisplay();
  });

  sortBySelect.addEventListener('change', updateProductDisplay);

  // Initial display
  currentProducts = [...products];
  updateProductDisplay();
});