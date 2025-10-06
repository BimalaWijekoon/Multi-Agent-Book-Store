# Sri Lankan Bookstore Updates - October 6, 2025

## 🇱🇰 Complete Localization to Sri Lankan Context

Two major updates have been implemented to make the simulation more realistic for Sri Lanka:

---

## 📊 UPDATE 1: Enhanced Customer Table in Agents Page

### What Changed:
The Agents page customer table now matches the Summary page layout, showing detailed budget breakdown.

### Before:
| ID | Name | Budget | Satisfaction | Preferred Genres | Status |
|----|------|--------|--------------|------------------|--------|
| customer_0 | Nancy Kumar | $100.00 | 0.75 | Fiction, Mystery | Happy |

### After:
| ID | Name | Initial Budget | Remaining Budget | Total Spent | Books Purchased | Satisfaction | Loyalty Level |
|----|------|----------------|------------------|-------------|-----------------|--------------|---------------|
| customer_0 | Nancy Kumar | Rs. 15,450.00 | Rs. 2,100.50 | Rs. 13,349.50 | 8 | 0.75 | Premium |

### New Columns:
1. **Initial Budget** - Starting budget (randomized Rs. 5,000-20,000)
2. **Remaining Budget** - What's left after purchases
3. **Total Spent** - Sum of all purchases
4. **Books Purchased** - Number of books bought
5. **Loyalty Level** - Customer loyalty status (New/Regular/Premium)

### Files Modified:
- `frontend/templates/agents.html` - Updated table headers
- `frontend/static/js/agents.js` - Updated DataTable columns and rendering logic

---

## 🇱🇰 UPDATE 2: Sri Lankan Books, Authors & Currency

### A. Sri Lankan Books & Authors

**Before (English Books):**
```
The Great Gatsby - F. Scott Fitzgerald
To Kill a Mockingbird - Harper Lee
1984 - George Orwell
Harry Potter - J.K. Rowling
```

**After (Sri Lankan Books):**
```
Gamperaliya - Martin Wickramasinghe
Viragaya - W.A. Silva
The Seven Moons of Maali Almeida - Shehan Karunatilaka
Madol Duwa - G.B. Senanayake
Funny Boy - Shyam Selvadurai
Running in the Family - Michael Ondaatje
The Village in the Jungle - Leonard Woolf
Chinaman - Shehan Karunatilaka
Island of a Thousand Mirrors - Nayomi Munaweera
```

**Complete Book List (48 titles):**
- Classic Sinhala literature (Gamperaliya, Kaliyugaya, Viragaya)
- Contemporary Sri Lankan fiction (Funny Boy, Cinnamon Gardens)
- International award-winners (The Seven Moons of Maali Almeida - Booker Prize 2022)
- Buddhist literature (Dharmapradipaya, Selalihini Sandeshaya)
- Children's classics (Madol Duwa, Ran Kirilli)
- Modern Sri Lankan novels (Chinaman, Island of a Thousand Mirrors)

### B. Currency Change: $ → Rs.

**Price Ranges:**

| Item | Before (USD) | After (LKR) | Multiplier |
|------|--------------|-------------|------------|
| Books | $10-$50 | Rs. 300-5,000 | ~100x |
| Customer Budget | $50-$200 | Rs. 5,000-20,000 | ~100x |
| Minimum Book Price | $5 | Rs. 300 | 60x |

**Conversion Rate:** Approximately 1 USD = 100 LKR (realistic for Sri Lankan market)

### C. Files Modified:

**1. Book Data:**
- `simulation/bookstore_model.py` (Lines 109-149)
  - 48 Sri Lankan book titles
  - 40+ Sri Lankan and international authors
  - Book prices: Rs. 300-5,000

**2. Customer Budgets:**
- `agents/customer_agent.py` (Line 60)
  - Random budget: Rs. 5,000-20,000
  - Realistic spending power for Sri Lanka

**3. Currency Display (All $ → Rs.):**
- `frontend/static/js/agents.js` - All price displays
- `frontend/static/js/summary.js` - All revenue/budget displays
- `frontend/app.py` - All logging statements
- `agents/customer_agent.py` - All logger messages
- `agents/book_agent.py` - All logger messages
- `agents/employee_agent.py` - All logger messages

**4. Price Constraints:**
- `agents/book_agent.py` (Line 286)
  - Minimum price: Rs. 300 (instead of $5)

---

## 📖 Sample Sri Lankan Books by Category

### Classic Sinhala Literature:
- **Gamperaliya** - Martin Wickramasinghe (The Changing Village)
- **Viragaya** - W.A. Silva (The Devolution)
- **Kaliyugaya** - Martin Wickramasinghe (The Dark Age)
- **Yuganthaya** - Ediriweera Sarachchandra (The End of an Era)

### Contemporary English Fiction:
- **The Seven Moons of Maali Almeida** - Shehan Karunatilaka (Booker Prize 2022)
- **Funny Boy** - Shyam Selvadurai
- **Cinnamon Gardens** - Shyam Selvadurai
- **Running in the Family** - Michael Ondaatje
- **Island of a Thousand Mirrors** - Nayomi Munaweera

### Award-Winning Cricket Fiction:
- **Chinaman** - Shehan Karunatilaka (Commonwealth Book Prize)

### Historical & Buddhist Literature:
- **The Village in the Jungle** - Leonard Woolf (Colonial era)
- **Dharmapradipaya** - Various Buddhist Scholars
- **Selalihini Sandeshaya** - Thotagamuwe Sri Rahula Thera

### Children's Literature:
- **Madol Duwa** - G.B. Senanayake (Island of Adventure)
- **Ran Kirilli** - Simon Nawagattegama (Golden Peacock)
- **The Story of Sigiri** - Sybil Wettasinghe

---

## 🎯 Expected Simulation Output

### Console Output:
```
Customer customer_0 (Nancy Kumar) initialized with random budget Rs. 15,450.00
Customer customer_1 (Eden Hassan) initialized with random budget Rs. 7,890.50

Step 1/30 | Revenue=Rs. 0.00 | Books Sold=0 | Satisfaction=0.50 | Msgs=0

Customer customer_0 browsing books...
Customer customer_0 selected book book_5
✓ SALE COMPLETED: Gamperaliya sold to customer_0 for Rs. 850.00

Step 30/30 | Revenue=Rs. 145,320.50 | Books Sold=38 | Satisfaction=0.68 | Msgs=156
🎉 Simulation completed!
📊 Final Revenue: Rs. 145,320.50
📖 Books Sold: 38
```

### Summary Page Display:
```
💰 Total Revenue: Rs. 145,320.50
📖 Books Sold: 38
😊 Avg Satisfaction: 0.68

Top Performing Books:
1. Gamperaliya - 8 sales - Rs. 6,800.00
2. The Seven Moons of Maali Almeida - 6 sales - Rs. 11,400.00
3. Chinaman - 5 sales - Rs. 7,500.00

Customer Details:
Nancy Kumar    | Rs. 15,450.00 | Rs. 2,100.00 | Rs. 13,350.00 | 8 books
Eden Hassan    | Rs. 7,890.50  | Rs. 1,200.50 | Rs. 6,690.00  | 3 books
```

---

## 🌟 Cultural Authenticity Features

### 1. **Language Mix**
- Sinhala titles (Gamperaliya, Viragaya)
- English titles by Sri Lankan authors (Funny Boy, Chinaman)
- Tamil-influenced names in books

### 2. **Literary Heritage**
- Ancient Buddhist texts (Selalihini Sandeshaya)
- Colonial-era literature (The Village in the Jungle)
- Post-independence classics (Martin Wickramasinghe collection)
- Contemporary award-winners (Shehan Karunatilaka's works)

### 3. **Realistic Pricing**
- Book prices: Rs. 300-5,000 (realistic for Sri Lankan bookstores)
- Budget range: Rs. 5,000-20,000 (typical monthly book budget)
- Price adjustments consider Sri Lankan market dynamics

### 4. **Author Diversity**
- Sinhala authors (Martin Wickramasinghe, W.A. Silva)
- Tamil authors (Shyam Selvadurai)
- Burgher authors (Michael Ondaatje)
- International authors with Sri Lankan roots (Nayomi Munaweera)

---

## 📊 Comparison Table

| Aspect | Before (International) | After (Sri Lankan) |
|--------|------------------------|---------------------|
| **Books** | The Great Gatsby, 1984 | Gamperaliya, Viragaya |
| **Authors** | F. Scott Fitzgerald | Martin Wickramasinghe |
| **Currency** | USD ($) | LKR (Rs.) |
| **Book Prices** | $10-$50 | Rs. 300-5,000 |
| **Customer Budget** | $50-$200 | Rs. 5,000-20,000 |
| **Cultural Context** | Western literature | Sri Lankan literature |
| **Languages** | English only | Sinhala, Tamil, English |
| **Literary Periods** | 20th century Western | Ancient to contemporary Sri Lankan |

---

## 🚀 Testing the Changes

### Run New Simulation:
```powershell
python launch_dashboard.py
```

### What to Check:

1. **Console Output:**
   - ✅ Budgets show "Rs." instead of "$"
   - ✅ Book titles are Sri Lankan
   - ✅ Prices range Rs. 300-5,000

2. **Agents Page:**
   - ✅ Customer table has 8 columns
   - ✅ Shows Initial Budget, Remaining, Spent
   - ✅ All currency displays use "Rs."

3. **Summary Page:**
   - ✅ Book titles are Sri Lankan
   - ✅ Revenue shows "Rs."
   - ✅ All price displays use "Rs."

4. **Cultural Accuracy:**
   - ✅ Mix of Sinhala and English titles
   - ✅ Recognizable Sri Lankan authors
   - ✅ Realistic pricing for Sri Lankan market

---

## 🎉 Benefits of Localization

1. **Cultural Relevance** - Simulation reflects Sri Lankan literary culture
2. **Educational Value** - Showcases Sri Lankan literature diversity
3. **Realistic Economics** - Uses appropriate currency and pricing
4. **Better Testing** - More relatable data for Sri Lankan users
5. **Literary Awareness** - Promotes Sri Lankan authors and books

---

**🇱🇰 The simulation is now fully localized for the Sri Lankan context with authentic books, authors, and economic realism!**
