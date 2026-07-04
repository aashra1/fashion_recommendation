// Product Functions

let currentPage = 1;
let currentFilters = {};
let totalProducts = 0;

function productImageFallback(width = 300, height = 400, label = "NepaliFashion") {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
      <rect width="100%" height="100%" fill="#f3f4f6"/>
      <rect x="24" y="24" width="${width - 48}" height="${height - 48}" rx="12" fill="#ffffff" stroke="#d1d5db"/>
      <text x="50%" y="48%" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#6d28d9">${label}</text>
      <text x="50%" y="56%" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#6b7280">Fashion image</text>
    </svg>`;
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

function getProductImage(product, width = 300, height = 400) {
  return product.image_url || product.thumbnail_url || productImageFallback(width, height);
}

function normalizeFilters(filters = {}) {
  const normalized = { ...filters };
  delete normalized.page;
  Object.keys(normalized).forEach((key) => {
    if (normalized[key] === "" || normalized[key] === null || normalized[key] === undefined) {
      delete normalized[key];
    }
  });
  return normalized;
}

async function loadProducts(page = 1, filters = {}) {
  currentPage = page;
  currentFilters = normalizeFilters(filters);

  const params = new URLSearchParams({
    page: page,
    page_size: 20,
    ...currentFilters,
  });

  try {
    const products = await api.get(`/products?${params.toString()}`);

    if (products && products.length > 0) {
      totalProducts = products.length;
      renderProductGrid(products);
    } else {
      renderEmptyState();
    }
  } catch (error) {
    console.error("Failed to load products:", error);
    showToast("Failed to load products", "error");
  }
}

async function loadProductDetail(productId) {
  try {
    const product = await api.get(`/products/${productId}`);
    renderProductDetail(product);

    // Log view for product detail page
    if (isAuthenticated()) {
      await interactionTracker.logView(productId, 0);
    }

    // Load similar products
    loadSimilarProducts(productId);
  } catch (error) {
    console.error("Failed to load product:", error);
    showToast("Product not found", "error");
    navigateTo("products");
  }
}

async function loadSimilarProducts(productId) {
  try {
    const similar = await api.get(
      `/recommendations/similar/${productId}?limit=10`,
    );
    renderSimilarProducts(similar);
  } catch (error) {
    console.error("Failed to load similar products:", error);
  }
}

async function loadPopularProducts(limit = 10) {
  try {
    const products = await api.get(`/products/popular/?limit=${limit}`);
    return products;
  } catch (error) {
    console.error("Failed to load popular products:", error);
    return [];
  }
}

async function loadTrendingProducts(limit = 10) {
  try {
    const products = await api.get(`/products/trending/?limit=${limit}`);
    return products;
  } catch (error) {
    console.error("Failed to load trending products:", error);
    return [];
  }
}

// Render Functions
function renderProductGrid(products) {
  const content = document.getElementById("content");
  const selectedCategories = (currentFilters.category || "").split(",").filter(Boolean);
  const selectedStyles = (currentFilters.style || "").split(",").filter(Boolean);
  const selectedSort = currentFilters.sort_by || "popularity";

  let html = `
        <div class="container mx-auto px-4 py-8">
            <div class="products-layout">
                <!-- Filters Sidebar -->
                <div class="filters-column">
                    <div class="filter-section">
                        <h3>Filters</h3>
                        <div class="filter-group">
                            <label>Category</label>
                            ${[
                              "Men",
                              "Women",
                              "Kids",
                              "Traditional",
                              "Accessories",
                            ]
                              .map(
                                (cat) => `
                                <label>
                                    <input type="checkbox" value="${cat}" onchange="applyFilters()" class="filter-category" ${selectedCategories.includes(cat) ? "checked" : ""}>
                                    ${cat}
                                </label>
                            `,
                              )
                              .join("")}
                        </div>
                        <div class="filter-group">
                            <label>Style</label>
                            ${[
                              "Casual",
                              "Formal",
                              "Sport",
                              "Traditional",
                              "Winter",
                            ]
                              .map(
                                (style) => `
                                <label>
                                    <input type="checkbox" value="${style}" onchange="applyFilters()" class="filter-style" ${selectedStyles.includes(style) ? "checked" : ""}>
                                    ${style}
                                </label>
                            `,
                              )
                              .join("")}
                        </div>
                        <div class="filter-group">
                            <label>Price Range (NPR)</label>
                            <div class="price-range">
                                <input type="number" placeholder="Min" id="price-min" onchange="applyFilters()" value="${currentFilters.min_price || ""}">
                                <span>to</span>
                                <input type="number" placeholder="Max" id="price-max" onchange="applyFilters()" value="${currentFilters.max_price || ""}">
                            </div>
                        </div>
                        <button onclick="clearFilters()" class="w-full mt-4 px-4 py-2 bg-gray-100 rounded hover:bg-gray-200">
                            Clear Filters
                        </button>
                    </div>
                </div>
                
                <!-- Product Grid -->
                <div class="flex-1">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold">Products</h2>
                        <select onchange="applyFilters()" id="sort-by" class="px-3 py-2 border rounded">
                            <option value="popularity" ${selectedSort === "popularity" ? "selected" : ""}>Popularity</option>
                            <option value="price_asc" ${selectedSort === "price_asc" ? "selected" : ""}>Price: Low to High</option>
                            <option value="price_desc" ${selectedSort === "price_desc" ? "selected" : ""}>Price: High to Low</option>
                            <option value="newest" ${selectedSort === "newest" ? "selected" : ""}>Newest First</option>
                        </select>
                    </div>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        ${products.map((product) => createProductCard(product)).join("")}
                    </div>
                    
                    <!-- Pagination -->
                    <div class="flex justify-center mt-8 space-x-2">
                        <button onclick="goToProductsPage(${currentPage - 1})" 
                                class="px-4 py-2 border rounded ${currentPage === 1 ? "opacity-50 cursor-not-allowed" : "hover:bg-gray-100"}"
                                ${currentPage === 1 ? "disabled" : ""}>
                            Previous
                        </button>
                        <span class="px-4 py-2">Page ${currentPage}</span>
                        <button onclick="goToProductsPage(${currentPage + 1})" 
                                class="px-4 py-2 border rounded hover:bg-gray-100">
                            Next
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

  content.innerHTML = html;

  // Track products for view logging
  products.forEach((product) => {
    interactionTracker.trackProduct(product.id);
  });
}

function createProductCard(product) {
  const discount = product.discount_price
    ? Math.round(
        ((product.price - product.discount_price) / product.price) * 100,
      )
    : 0;

  const tags = Array.isArray(product.tags) ? product.tags : [];
  const imageUrl = getProductImage(product);

  return `
        <div class="product-card bg-white rounded-lg shadow-md overflow-hidden" 
             data-product-id="${product.id}" onclick="handleProductClick('${product.id}')">
            <div class="product-image-container">
                <img src="${imageUrl}" 
                     alt="${product.name}"
                     loading="lazy"
                     onerror="this.onerror=null;this.src='${productImageFallback()}'">
                ${discount > 0 ? `<span class="badge badge-discount absolute top-2 right-2">${discount}% OFF</span>` : ""}
            </div>
            <div class="p-4">
                <div class="flex items-start justify-between">
                    <h3 class="text-lg font-semibold text-gray-800 truncate">${product.name}</h3>
                </div>
                <p class="text-sm text-gray-600 mt-1">${product.brand || "Nepali Brand"}</p>
                <div class="flex items-center mt-2">
                    <span class="text-xl font-bold text-purple-600">Rs. ${product.discount_price || product.price}</span>
                    ${product.discount_price ? `<span class="text-sm text-gray-400 line-through ml-2">Rs. ${product.price}</span>` : ""}
                </div>
                ${
                  tags.length > 0
                    ? `
                    <div class="flex flex-wrap gap-1 mt-2">
                        ${tags
                          .slice(0, 3)
                          .map(
                            (tag) => `
                            <span class="text-xs px-2 py-1 bg-gray-100 rounded-full">${tag}</span>
                        `,
                          )
                          .join("")}
                    </div>
                `
                    : ""
                }
                <div class="flex items-center justify-between mt-3">
                    <button onclick="event.stopPropagation(); handleWishlist('${product.id}')" 
                            class="px-3 py-1 text-sm bg-pink-50 text-pink-600 rounded hover:bg-pink-100">
                        ♥ Wishlist
                    </button>
                    <button onclick="event.stopPropagation(); handleAddToCart('${product.id}')" 
                            class="px-4 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700">
                        Add to Cart
                    </button>
                </div>
            </div>
        </div>
    `;
}

function renderProductDetail(product) {
  const content = document.getElementById("content");
  const discount = product.discount_price
    ? Math.round(
        ((product.price - product.discount_price) / product.price) * 100,
      )
    : 0;

  const tags = Array.isArray(product.tags) ? product.tags : [];
  const styles = Array.isArray(product.style) ? product.style : [];
  const colors = Array.isArray(product.color) ? product.color : [];
  const sizes = Array.isArray(product.size) ? product.size : [];
  const imageUrl = getProductImage(product, 600, 800);

  let html = `
        <div class="container mx-auto px-4 py-8">
            <div class="product-detail-container">
                <!-- Product Image -->
                <div class="product-detail-image">
                    <img src="${imageUrl}" 
                         alt="${product.name}"
                         onerror="this.onerror=null;this.src='${productImageFallback(600, 800)}'">
                </div>
                
                <!-- Product Info -->
                <div class="product-detail-info">
                    <h1>${product.name}</h1>
                    <div class="brand">${product.brand || "Nepali Brand"}</div>
                    
                    <div class="price">
                        Rs. ${product.discount_price || product.price}
                        ${
                          product.discount_price
                            ? `
                            <span class="original-price">Rs. ${product.price}</span>
                            <span class="badge badge-discount ml-2">${discount}% OFF</span>
                        `
                            : ""
                        }
                    </div>
                    
                    <div class="flex items-center mt-2">
                        <span class="text-yellow-400">★</span>
                        <span class="text-sm text-gray-600 ml-1">${product.rating || 0} (${product.total_ratings || 0} reviews)</span>
                    </div>
                    
                    <div class="description mt-4">
                        <p>${product.description || "No description available."}</p>
                    </div>
                    
                    ${
                      styles.length > 0
                        ? `
                        <div class="mt-4">
                            <h4 class="font-semibold">Style</h4>
                            <div class="flex flex-wrap gap-2 mt-1">
                                ${styles.map((s) => `<span class="tag">${s}</span>`).join("")}
                            </div>
                        </div>
                    `
                        : ""
                    }
                    
                    ${
                      tags.length > 0
                        ? `
                        <div class="mt-4">
                            <h4 class="font-semibold">Tags</h4>
                            <div class="flex flex-wrap gap-2 mt-1">
                                ${tags.map((t) => `<span class="tag">${t}</span>`).join("")}
                            </div>
                        </div>
                    `
                        : ""
                    }
                    
                    ${
                      colors.length > 0
                        ? `
                        <div class="mt-4">
                            <h4 class="font-semibold">Colors</h4>
                            <div class="flex flex-wrap gap-2 mt-1">
                                ${colors.map((c) => `<span class="tag">${c}</span>`).join("")}
                            </div>
                        </div>
                    `
                        : ""
                    }
                    
                    ${
                      sizes.length > 0
                        ? `
                        <div class="mt-4">
                            <h4 class="font-semibold">Sizes</h4>
                            <div class="flex flex-wrap gap-2 mt-1">
                                ${sizes.map((s) => `<span class="tag">${s}</span>`).join("")}
                            </div>
                        </div>
                    `
                        : ""
                    }
                    
                    <div class="actions mt-6">
                        <button onclick="handleWishlist('${product.id}')" 
                                class="btn-wishlist">
                            ♥ Add to Wishlist
                        </button>
                        <button onclick="handleAddToCart('${product.id}')" 
                                class="btn-cart">
                            🛒 Add to Cart
                        </button>
                    </div>
                    
                    <div class="mt-4 text-sm text-gray-500">
                        Category: ${product.category} ${product.sub_category ? `→ ${product.sub_category}` : ""}
                        ${product.gender ? `• ${product.gender}` : ""}
                    </div>
                </div>
            </div>
            
            <!-- Similar Products -->
            <div id="similar-products" class="mt-12">
                <!-- Will be populated by JavaScript -->
            </div>
        </div>
    `;

  content.innerHTML = html;
}

function renderSimilarProducts(products) {
  const container = document.getElementById("similar-products");
  if (!products || products.length === 0) {
    if (container) container.innerHTML = "";
    return;
  }

  let html = `
        <div class="recommendation-section rounded-lg p-6">
            <h2 class="text-2xl font-bold">You May Also Like</h2>
            <p class="subtitle">Products similar to this one</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                ${products.map((product) => createProductCard(product)).join("")}
            </div>
        </div>
    `;

  container.innerHTML = html;
}

function renderEmptyState() {
  const content = document.getElementById("content");
  content.innerHTML = `
        <div class="container mx-auto px-4 py-16 text-center">
            <div class="text-6xl mb-4">🛍️</div>
            <h2 class="text-2xl font-bold text-gray-700">No Products Found</h2>
            <p class="text-gray-500 mt-2">Try adjusting your filters</p>
            <button onclick="clearFilters()" class="mt-4 px-6 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                Clear Filters
            </button>
        </div>
    `;
}

// Filter Functions
function applyFilters() {
  const filters = {
    category: [],
    style: [],
    sort_by: document.getElementById("sort-by")?.value || "popularity",
  };

  // Get selected categories
  document.querySelectorAll(".filter-category:checked").forEach((cb) => {
    filters.category.push(cb.value);
  });

  // Get selected styles
  document.querySelectorAll(".filter-style:checked").forEach((cb) => {
    filters.style.push(cb.value);
  });

  // Get price range
  const minPrice = document.getElementById("price-min")?.value;
  const maxPrice = document.getElementById("price-max")?.value;

  if (minPrice) filters.min_price = parseFloat(minPrice);
  if (maxPrice) filters.max_price = parseFloat(maxPrice);

  // Convert arrays to comma-separated strings for API
  if (filters.category.length > 0)
    filters.category = filters.category.join(",");
  else delete filters.category;

  if (filters.style.length > 0) filters.style = filters.style.join(",");
  else delete filters.style;

  navigateTo("products", filters);
}

function goToProductsPage(page) {
  navigateTo("products", { ...currentFilters, page });
}

function clearFilters() {
  document.querySelectorAll(".filter-category, .filter-style").forEach((cb) => {
    cb.checked = false;
  });
  const minPrice = document.getElementById("price-min");
  const maxPrice = document.getElementById("price-max");
  if (minPrice) minPrice.value = "";
  if (maxPrice) maxPrice.value = "";

  navigateTo("products", {});
}

// Interaction Handlers
async function handleWishlist(productId) {
  if (!isAuthenticated()) {
    showToast("Please login to add to wishlist", "error");
    navigateTo("login");
    return;
  }
  await interactionTracker.logInteraction(productId, "WISHLIST_ADD");
}

async function handleAddToCart(productId) {
  if (!isAuthenticated()) {
    showToast("Please login to add to cart", "error");
    navigateTo("login");
    return;
  }
  await interactionTracker.logInteraction(productId, "CART_ADD");
}

async function handleProductClick(productId) {
  if (isAuthenticated()) {
    await interactionTracker.logInteraction(productId, "CLICK", null, false);
  }
  navigateTo("product", { id: productId });
}

window.applyFilters = applyFilters;
window.clearFilters = clearFilters;
window.goToProductsPage = goToProductsPage;
window.handleWishlist = handleWishlist;
window.handleAddToCart = handleAddToCart;
window.handleProductClick = handleProductClick;
