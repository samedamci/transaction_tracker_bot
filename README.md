# Transaction Tracker Bot

[Telegram bot](https://t.me/transaction_tracker_bot) to track Bitcoin transactions.

## Usage

Use `/start` or `/help` option to display available commands.

## Self-hosting

+ Clone this repo.
```
$ git clone https://github.com/samedamci/transaction_tracker_bot && cd transaction_tracker_bot
```
+ Install required modules.
```
$ pip3 install --user -r requirements.txt
```
+ Create `environment` file with your bot token and instance URL.
```
TOKEN=your_token_here
```
+ Start bot with `python3 main.py`.

### With Docker

+ Build image itself.
```
# docker build -t samedamci/transaction_tracker_bot .
```
+ Run bot in container.
```
# docker run --rm -d -e TOKEN='your_token_here' --name transaction_tracker_bot samedamci/transaction_tracker_bot
```
