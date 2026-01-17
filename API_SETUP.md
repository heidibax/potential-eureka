# API Setup Guide

This guide explains how to connect your HTML/CSS/JavaScript frontend to the Python backend using Flask REST API.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python app.py
```

The API will be running at `http://localhost:5000`

### 3. Test the API

Open `example_frontend.html` in your browser to test the API endpoints interactively.

## API Endpoints

### Base URL
All endpoints are prefixed with `/api`

### User Management

- **POST** `/api/users` - Create a new user
  ```json
  {
    "username": "Player1",
    "email": "player1@example.com",
    "initial_balance": 100.0
  }
  ```

- **GET** `/api/users/<user_id>` - Get user information
- **GET** `/api/users` - List all users

### Portfolio Management

- **GET** `/api/users/<user_id>/portfolio` - Get user's portfolio
- **POST** `/api/users/<user_id>/portfolio/buy` - Buy stocks
  ```json
  {
    "ticker": "AAPL",
    "shares": 2
  }
  ```
- **POST** `/api/users/<user_id>/portfolio/sell` - Sell stocks
  ```json
  {
    "ticker": "AAPL",
    "shares": 1
  }
  ```

### Stock Information

- **GET** `/api/stocks` - Get all available stocks with prices
- **GET** `/api/stocks/<ticker>/earnings` - Get earnings data for a stock

### Game Scoring

- **GET** `/api/game/scores` - Get game scores for all companies
- **GET** `/api/users/<user_id>/score` - Get user's total score based on portfolio

### Social Features

- **POST** `/api/users/<user_id>/follow/<target_user_id>` - Follow a user
- **POST** `/api/users/<user_id>/unfollow/<target_user_id>` - Unfollow a user
- **GET** `/api/users/<user_id>/messages` - Get user's messages
- **POST** `/api/users/<user_id>/messages` - Send a message
  ```json
  {
    "recipient_id": "user_id_here",
    "message": "Hello!"
  }
  ```

### Health Check

- **GET** `/api/health` - Check if API is running

## Frontend Integration Example

### Using Fetch API (JavaScript)

```javascript
// Base URL
const API_BASE = 'http://localhost:5000/api';

// Create a user
async function createUser(username, email) {
    const response = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            email: email,
            initial_balance: 100.0
        })
    });
    return await response.json();
}

// Get available stocks
async function getStocks() {
    const response = await fetch(`${API_BASE}/stocks`);
    return await response.json();
}

// Buy a stock
async function buyStock(userId, ticker, shares) {
    const response = await fetch(`${API_BASE}/users/${userId}/portfolio/buy`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ticker: ticker,
            shares: shares
        })
    });
    return await response.json();
}

// Get user score
async function getUserScore(userId) {
    const response = await fetch(`${API_BASE}/users/${userId}/score`);
    return await response.json();
}
```

### Using jQuery (if you prefer)

```javascript
// Create a user
$.ajax({
    url: 'http://localhost:5000/api/users',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        username: 'Player1',
        email: 'player1@example.com',
        initial_balance: 100.0
    }),
    success: function(data) {
        console.log('User created:', data);
    }
});
```

## CORS Configuration

The API has CORS enabled, so your frontend can make requests from any origin. This is configured in `app.py` with:

```python
CORS(app)  # Enable CORS for all routes
```

## Stock Pricing

Stocks are priced based on their category:
- **Premium Picks**: $15
- **Mid-Tier**: $10
- **Wildcards**: $5
- **Risky Plays**: $3

## Error Handling

All endpoints return JSON responses. Errors follow this format:

```json
{
    "error": "Error message here"
}
```

Successful responses return the requested data directly.

## Next Steps

1. **Database Integration**: Currently, users are stored in memory. For production, integrate a database (SQLite, PostgreSQL, etc.)

2. **Authentication**: Add user authentication (JWT tokens, sessions, etc.)

3. **Real-time Updates**: Consider WebSockets for real-time score updates

4. **Caching**: Cache stock data and earnings information to reduce API calls

5. **Rate Limiting**: Add rate limiting to prevent abuse

## Troubleshooting

- **Port already in use**: Change the port in `app.py` (last line)
- **Import errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
- **CORS errors**: The API has CORS enabled, but if you still see errors, check your browser console
