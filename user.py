from datetime import datetime

class User:
    def __init__(self, user_id, username, email, initial_balance):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = datetime.now()

        self.initial_balance = 100.0
        self.balance = initial_balance

        self.portfolio = Portfolio()
        self.followers = set()
        self.following = set()

        self.inbox = []

    def create_user(self, user_id, username, email, initial_balance):
        return User(user_id, username, email, initial_balance)
    
    def delete_user(self):
        del self

    def get_user(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "initial_balance": self.initial_balance,
            "balance": self.balance,
            "portfolio": self.portfolio.holdings,
            "followers": list(self.followers),
            "following": list(self.following),
            "inbox": self.inbox
        }
    def update_balance(self, amount):
        self.balance += amount

class Portfolio:
    def __init__(self):
        self.holdings = {}  # key: ticker, value: number of shares

    def add_stock(self, ticker, shares):
        if ticker in self.holdings:
            self.holdings[ticker] += shares
        else:
            self.holdings[ticker] = shares

    def remove_stock(self, ticker, shares):
        if ticker in self.holdings and self.holdings[ticker] >= shares:
            self.holdings[ticker] -= shares
            if self.holdings[ticker] == 0:
                del self.holdings[ticker]
        else:
            raise ValueError("Not enough shares to sell")
    
    def get_holdings(self):
        return self.holdings

    def can_afford(self, price_per_share, shares):
        total_cost = price_per_share * shares
        return total_cost <= self.balance

class SocialFeatures:
    def follow(self, user_to_follow):
        self.following.add(user_to_follow.user_id)
        user_to_follow.followers.add(self.user_id)

    def unfollow(self, user_to_unfollow):
        self.following.discard(user_to_unfollow.user_id)
        user_to_unfollow.followers.discard(self.user_id)

    def send_message(self, recipient, message):
        timestamp = datetime.now()
        recipient.inbox.append({
            "from": self.user_id,
            "message": message,
            "timestamp": timestamp
        })
    
    def receive_messages(self):
        return self.inbox

