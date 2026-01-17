from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from user import User, Portfolio
import uuid
from datetime import datetime
import json

# Import game logic from main.py
from main import (
    COMPANIES, POINTS, premium_picks, mid_tier, wildcards, risky_plays,
    eps_outcome, score_company_game, stock_market_reaction, price_change_1month,
    earnings_rows, game_score
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage (replace with database in production)
users = {}
user_counter = 0

# Stock pricing (simplified - in production, fetch real-time prices)
STOCK_PRICES = {
    "premium": 15,
    "mid_tier": 10,
    "wildcard": 5,
    "risky": 3
}

def get_stock_price(ticker):
    """Get the price category for a stock"""
    if ticker in premium_picks:
        return STOCK_PRICES["premium"]
    elif ticker in mid_tier:
        return STOCK_PRICES["mid_tier"]
    elif ticker in wildcards:
        return STOCK_PRICES["wildcard"]
    elif ticker in risky_plays:
        return STOCK_PRICES["risky"]
    return 0

#  USER ENDPOINTS 

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    global user_counter
    data = request.json
    
    user_id = str(uuid.uuid4())
    username = data.get('username')
    email = data.get('email', '')
    initial_balance = data.get('initial_balance', 100.0)
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    user = User(user_id, username, email, initial_balance)
    users[user_id] = user
    
    user_data = user.get_user()
    # Convert datetime to string for JSON serialization
    if 'created_at' in user_data and isinstance(user_data['created_at'], datetime):
        user_data['created_at'] = user_data['created_at'].isoformat()
    
    return jsonify(user_data), 201

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = users[user_id].get_user()
    # Convert datetime to string for JSON serialization
    if 'created_at' in user_data and isinstance(user_data['created_at'], datetime):
        user_data['created_at'] = user_data['created_at'].isoformat()
    # Convert datetime objects in inbox
    if 'inbox' in user_data:
        for msg in user_data['inbox']:
            if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
                msg['timestamp'] = msg['timestamp'].isoformat()
    
    return jsonify(user_data)

@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users"""
    users_list = []
    for user in users.values():
        user_data = user.get_user()
        # Convert datetime to string for JSON serialization
        if 'created_at' in user_data and isinstance(user_data['created_at'], datetime):
            user_data['created_at'] = user_data['created_at'].isoformat()
        # Convert datetime objects in inbox
        if 'inbox' in user_data:
            for msg in user_data['inbox']:
                if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
                    msg['timestamp'] = msg['timestamp'].isoformat()
        users_list.append(user_data)
    return jsonify(users_list)

#  PORTFOLIO ENDPOINTS 

@app.route('/api/users/<user_id>/portfolio', methods=['GET'])
def get_portfolio(user_id):
    """Get user's portfolio"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[user_id]
    portfolio_data = {
        'holdings': user.portfolio.holdings,
        'balance': user.balance,
        'total_value': user.balance  # Simplified - add stock value calculation
    }
    
    return jsonify(portfolio_data)

@app.route('/api/users/<user_id>/portfolio/buy', methods=['POST'])
def buy_stock(user_id):
    """Buy stocks for user's portfolio"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    ticker = data.get('ticker', '').upper()
    shares = int(data.get('shares', 1))
    
    if ticker not in COMPANIES:
        return jsonify({'error': f'Stock {ticker} not available'}), 400
    
    user = users[user_id]
    price_per_share = get_stock_price(ticker)
    total_cost = price_per_share * shares
    
    if not user.can_afford(price_per_share, shares):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    user.portfolio.add_stock(ticker, shares)
    user.update_balance(-total_cost)
    
    return jsonify({
        'message': f'Bought {shares} shares of {ticker}',
        'balance': user.balance,
        'portfolio': user.portfolio.holdings
    })

@app.route('/api/users/<user_id>/portfolio/sell', methods=['POST'])
def sell_stock(user_id):
    """Sell stocks from user's portfolio"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    ticker = data.get('ticker', '').upper()
    shares = int(data.get('shares', 1))
    
    user = users[user_id]
    
    try:
        user.portfolio.remove_stock(ticker, shares)
        price_per_share = get_stock_price(ticker)
        total_revenue = price_per_share * shares
        user.update_balance(total_revenue)
        
        return jsonify({
            'message': f'Sold {shares} shares of {ticker}',
            'balance': user.balance,
            'portfolio': user.portfolio.holdings
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

#  STOCK/COMPANY ENDPOINTS 

@app.route('/api/stocks', methods=['GET'])
def get_available_stocks():
    """Get list of all available stocks with their prices"""
    stocks = []
    for ticker in COMPANIES:
        price = get_stock_price(ticker)
        category = "premium" if ticker in premium_picks else \
                   "mid_tier" if ticker in mid_tier else \
                   "wildcard" if ticker in wildcards else "risky"
        stocks.append({
            'ticker': ticker,
            'price': price,
            'category': category
        })
    
    return jsonify(stocks)

@app.route('/api/stocks/<ticker>/earnings', methods=['GET'])
def get_stock_earnings(ticker):
    """Get earnings data for a specific stock"""
    ticker = ticker.upper()
    if ticker not in COMPANIES:
        return jsonify({'error': 'Stock not found'}), 404
    
    try:
        earnings_data = earnings_rows(ticker)
        if earnings_data:
            return jsonify(earnings_data)
        else:
            return jsonify({'error': 'No earnings data available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#  GAME SCORING ENDPOINTS 

@app.route('/api/game/scores', methods=['GET'])
def get_game_scores():
    """Get game scores for all companies"""
    try:
        scores = game_score
        return jsonify(scores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/score', methods=['GET'])
def get_user_score(user_id):
    """Calculate and return user's total game score based on their portfolio"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user = users[user_id]
    portfolio = user.portfolio.holdings
    
    try:
        all_scores = game_score
        total_score = 0
        portfolio_scores = []
        
        for ticker, shares in portfolio.items():
            # Find score for this ticker
            ticker_score = next((s for s in all_scores if s['ticker'] == ticker), None)
            if ticker_score:
                score_value = ticker_score['game_score'] * shares  # Multiply by shares owned
                total_score += score_value
                portfolio_scores.append({
                    'ticker': ticker,
                    'shares': shares,
                    'score_per_share': ticker_score['game_score'],
                    'total_score': score_value,
                    'breakdown': ticker_score.get('breakdown', {})
                })
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'total_score': total_score,
            'portfolio_scores': portfolio_scores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#  SOCIAL ENDPOINTS 

@app.route('/api/users/<user_id>/follow/<target_user_id>', methods=['POST'])
def follow_user(user_id, target_user_id):
    """Follow another user"""
    if user_id not in users or target_user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    users[user_id].follow(users[target_user_id])
    return jsonify({'message': 'User followed successfully'})

@app.route('/api/users/<user_id>/unfollow/<target_user_id>', methods=['POST'])
def unfollow_user(user_id, target_user_id):
    """Unfollow another user"""
    if user_id not in users or target_user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    users[user_id].unfollow(users[target_user_id])
    return jsonify({'message': 'User unfollowed successfully'})

@app.route('/api/users/<user_id>/messages', methods=['GET'])
def get_messages(user_id):
    """Get user's inbox messages"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    messages = users[user_id].receive_messages()
    # Convert datetime objects to strings
    for msg in messages:
        if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
            msg['timestamp'] = msg['timestamp'].isoformat()
    
    return jsonify(messages)

@app.route('/api/users/<user_id>/messages', methods=['POST'])
def send_message(user_id):
    """Send a message to another user"""
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    recipient_id = data.get('recipient_id')
    message = data.get('message')
    
    if not recipient_id or recipient_id not in users:
        return jsonify({'error': 'Recipient not found'}), 404
    
    users[user_id].send_message(users[recipient_id], message)
    return jsonify({'message': 'Message sent successfully'})

#  HEALTH CHECK 

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

#  ROOT ROUTES 

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Fantasy Stock League API',
        'version': '1.0',
        'endpoints': {
            'health': '/api/health',
            'users': '/api/users',
            'stocks': '/api/stocks',
            'game_scores': '/api/game/scores',
            'example_frontend': '/example'
        },
        'documentation': 'See API_SETUP.md for full documentation',
        'example_frontend': 'Open example_frontend.html in your browser or visit /example'
    })

@app.route('/example', methods=['GET'])
def serve_example():
    """Serve the example frontend HTML file"""
    try:
        return send_from_directory('.', 'example_frontend.html')
    except:
        return jsonify({
            'error': 'Example file not found',
            'instructions': 'Open example_frontend.html directly in your browser (file://) or place it in a static folder'
        }), 404

# FRONTEND API ENDPOINTS

@app.route('/companies', methods=['GET'])
def get_companies():
    """Get all companies with their data"""
    companies = []
    try:
        for idx, (ticker, data) in enumerate(earnings_rows.items(), 1):
            company = {
                'id': idx,
                'name': ticker,
                'ticker': ticker,
                'earnings_date': data.get('Earnings Date', 'N/A'),
                'img': f'img/{ticker.lower()}.png',
                'score': game_score.get(ticker, 0),
                'breakdown': {
                    'eps_estimate': data.get('EPS Estimate', 'N/A'),
                    'eps_actual': data.get('Reported EPS', 'N/A'),
                    'eps_result': data.get('EPS Result', 'N/A'),
                    'surprise_pct': data.get('Surprise %', 'N/A'),
                    'bonus_flags': data.get('Bonus Flags', []),
                    'daily_pct_change': stock_market_reaction.get(ticker, 'N/A'),
                    'monthly_price_change': price_change_1month.get(ticker, 'N/A'),
                }
            }
            companies.append(company)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify(companies)

@app.route('/companies/<company_id>', methods=['GET'])
def get_company(company_id):
    """Get a single company by ID"""
    try:
        companies_list = list(earnings_rows.items())
        idx = int(company_id) - 1
        if idx < 0 or idx >= len(companies_list):
            return jsonify({'error': 'Company not found'}), 404
        
        ticker, data = companies_list[idx]
        company = {
            'id': idx + 1,
            'name': ticker,
            'ticker': ticker,
            'earnings_date': data.get('Earnings Date', 'N/A'),
            'img': f'img/{ticker.lower()}.png',
            'score': game_score.get(ticker, 0),
            'breakdown': {
                'eps_estimate': data.get('EPS Estimate', 'N/A'),
                'eps_actual': data.get('Reported EPS', 'N/A'),
                'eps_result': data.get('EPS Result', 'N/A'),
                'surprise_pct': data.get('Surprise %', 'N/A'),
                'bonus_flags': data.get('Bonus Flags', []),
                'daily_pct_change': stock_market_reaction.get(ticker, 'N/A'),
                'monthly_price_change': price_change_1month.get(ticker, 'N/A'),
            }
        }
        return jsonify(company)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (HTML, CSS, JS)"""
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
