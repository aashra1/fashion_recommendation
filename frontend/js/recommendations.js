// Recommendation Functions

async function loadPersonalizedRecommendations(limit = 20) {
  if (!isAuthenticated()) {
    return loadPopularProducts(limit);
  }

  try {
    const recommendations = await api.get(
      `/recommendations/personalized?limit=${limit}`,
    );
    return recommendations;
  } catch (error) {
    console.error("Failed to load personalized recommendations:", error);
    return loadPopularProducts(limit);
  }
}

function renderRecommendations(
  recommendations,
  title = "Your Personalized Picks",
) {
  const content = document.getElementById("content");

  if (!recommendations || recommendations.length === 0) {
    content.innerHTML = `
            <div class="container mx-auto px-4 py-16 text-center">
                <div class="text-6xl mb-4">🎯</div>
                <h2 class="text-2xl font-bold text-gray-700">Start Exploring!</h2>
                <p class="text-gray-500 mt-2">Browse products to get personalized recommendations</p>
                <button onclick="navigateTo('products')" class="mt-4 px-6 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                    Explore Products
                </button>
            </div>
        `;
    return;
  }

  let html = `
        <div class="container mx-auto px-4 py-8">
            <div class="recommendation-section rounded-lg p-8 mb-8">
                <div class="flex justify-between items-center mb-6">
                    <div>
                        <h2 class="text-3xl font-bold">${title}</h2>
                        <p class="text-gray-600 mt-1">Tailored just for you using AI</p>
                    </div>
                    ${
                      isAuthenticated()
                        ? `
                        <div class="text-sm text-purple-600 bg-purple-50 px-4 py-2 rounded-full">
                            🧠 AI-Powered
                        </div>
                    `
                        : ""
                    }
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    ${recommendations
                      .map((rec) => {
                        const product = rec.product || rec;
                        return createProductCard(product);
                      })
                      .join("")}
                </div>
            </div>
        </div>
    `;

  content.innerHTML = html;

  // Track products for view logging
  recommendations.forEach((rec) => {
    const product = rec.product || rec;
    interactionTracker.trackProduct(product.id);
  });
}

async function renderHomePage() {
  const content = document.getElementById("content");

  // Show loading state
  content.innerHTML = `
        <div class="flex justify-center items-center min-h-[400px]">
            <div class="spinner"></div>
        </div>
    `;

  try {
    // Load recommendations
    let recommendations = await loadPersonalizedRecommendations(20);

    // Load trending products
    const trending = await loadTrendingProducts(10);

    let html = `
            <div class="container mx-auto px-4 py-8">
                <!-- Hero Section -->
                <div class="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-8 text-white mb-8">
                    <div class="max-w-2xl">
                        <h1 class="text-4xl font-bold mb-2">Discover Your Style</h1>
                        <p class="text-purple-100 text-lg">AI-powered fashion recommendations for Nepal</p>
                        ${
                          !isAuthenticated()
                            ? `
                            <button onclick="navigateTo('register')" class="mt-4 px-6 py-2 bg-white text-purple-600 rounded-lg font-semibold hover:bg-purple-50">
                                Get Started
                            </button>
                        `
                            : ""
                        }
                    </div>
                </div>
                
                <!-- Personalized Recommendations -->
                <div id="recommendations-section">
        `;

    if (recommendations && recommendations.length > 0) {
      html += `
                <div class="recommendation-section rounded-lg p-8 mb-8">
                    <div class="flex justify-between items-center mb-6">
                        <div>
                            <h2 class="text-3xl font-bold">${isAuthenticated() ? "Your Personalized Picks" : "Popular Products"}</h2>
                            <p class="text-gray-600 mt-1">${isAuthenticated() ? "Tailored just for you" : "Most loved by our community"}</p>
                        </div>
                        ${
                          isAuthenticated()
                            ? `
                            <div class="text-sm text-purple-600 bg-purple-50 px-4 py-2 rounded-full">
                                🧠 AI-Powered
                            </div>
                        `
                            : ""
                        }
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                        ${recommendations
                          .map((rec) => {
                            const product = rec.product || rec;
                            return createProductCard(product);
                          })
                          .join("")}
                    </div>
                </div>
            `;
    }

    // Trending Section
    if (trending && trending.length > 0) {
      html += `
                <div class="mb-8">
                    <h2 class="text-2xl font-bold mb-4">🔥 Trending Now</h2>
                    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                        ${trending.map((product) => createProductCard(product)).join("")}
                    </div>
                </div>
            `;
    }

    html += `
                </div>
            </div>
        `;

    content.innerHTML = html;

    // Track products for view logging
    const allProducts = [
      ...(recommendations || []).map((rec) => rec.product || rec),
      ...(trending || []),
    ];
    allProducts.forEach((product) => {
      if (product && product.id) {
        interactionTracker.trackProduct(product.id);
      }
    });
  } catch (error) {
    console.error("Failed to load home page:", error);
    content.innerHTML = `
            <div class="container mx-auto px-4 py-16 text-center">
                <div class="text-6xl mb-4">😅</div>
                <h2 class="text-2xl font-bold text-gray-700">Oops! Something went wrong</h2>
                <p class="text-gray-500 mt-2">Please try refreshing the page</p>
                <button onclick="renderHomePage()" class="mt-4 px-6 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                    Retry
                </button>
            </div>
        `;
  }
}
