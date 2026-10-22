
import csv
import urllib.request
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    yf = None


TICKER_URL = (
    "https://raw.githubusercontent.com/datasets/"
    "s-and-p-500-companies/master/data/constituents.csv"
)

OUTPUT_FILE = "portfolio_summary.csv"


def load_tickers():
    """Load valid ticker symbols from the provided dataset."""
    try:
        with urllib.request.urlopen(TICKER_URL, timeout=15) as response:
            text = response.read().decode("utf-8-sig")

        reader = csv.DictReader(text.splitlines())
        tickers = {
            row["Symbol"].strip().upper()
            for row in reader
            if row.get("Symbol")
        }

        if tickers:
            print("S&P 500 ticker dataset loaded.")
            return tickers

    except Exception as error:
        print("Could not download ticker dataset:", error)

    print("Using a small backup ticker list.")
    return {"AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"}


def get_current_price(ticker):
    """Try to get a recent market price."""
    if yf is not None:
        try:
            yahoo_ticker = ticker.replace(".", "-")
            history = yf.Ticker(yahoo_ticker).history(
                period="1d",
                interval="1m"
            )

            if not history.empty:
                price = float(history["Close"].dropna().iloc[-1])

                if price > 0:
                    return price, "Retrieved market data"

        except Exception:
            pass

    print("Live price unavailable for", ticker)

    while True:
        try:
            price = float(input("Enter current price manually: $"))

            if price > 0:
                return price, "Manually entered price"

            print("Price must be greater than zero.")

        except ValueError:
            print("Please enter a valid number.")


def get_positive_number(message):
    """Read a positive numeric value."""
    while True:
        try:
            value = float(input(message))

            if value > 0:
                return value

            print("Value must be greater than zero.")

        except ValueError:
            print("Please enter a valid number.")


def add_holding(portfolio, valid_tickers):
    """Collect one stock holding from the user."""
    ticker = input("Enter stock ticker: ").strip().upper()

    if ticker not in valid_tickers:
        print("Ticker not found in the loaded dataset.")
        return

    buy_price = get_positive_number("Enter purchase price per share ($): ")
    shares = get_positive_number("Enter number of shares: ")

    current_price, price_source = get_current_price(ticker)

    portfolio.append({
        "ticker": ticker,
        "buy_price": buy_price,
        "shares": shares,
        "current_price": current_price,
        "price_source": price_source
    })

    print("Holding added successfully!")


def calculate_portfolio(portfolio):
    """Calculate and display each holding's performance."""
    total_invested = 0.0
    total_market_value = 0.0

    print("\n" + "=" * 95)
    print("STOCK PORTFOLIO PERFORMANCE SUMMARY")
    print("=" * 95)

    print(
        f"{'Ticker':<10}{'Shares':>10}{'Buy Price':>15}"
        f"{'Current':>15}{'Market Value':>18}{'Gain/Loss %':>15}"
    )

    for holding in portfolio:
        invested = holding["buy_price"] * holding["shares"]
        market_value = holding["current_price"] * holding["shares"]
        gain_loss = market_value - invested
        percentage = (gain_loss / invested) * 100

        total_invested += invested
        total_market_value += market_value

        print(
            f"{holding['ticker']:<10}"
            f"{holding['shares']:>10.2f}"
            f"{holding['buy_price']:>15.2f}"
            f"{holding['current_price']:>15.2f}"
            f"{market_value:>18.2f}"
            f"{percentage:>14.2f}%"
        )

        holding["invested"] = invested
        holding["market_value"] = market_value
        holding["gain_loss"] = gain_loss
        holding["percentage"] = percentage

    total_gain_loss = total_market_value - total_invested

    if total_invested:
        total_percentage = total_gain_loss / total_invested * 100
    else:
        total_percentage = 0.0

    print("-" * 95)
    print(f"Total invested:     ${total_invested:,.2f}")
    print(f"Current value:      ${total_market_value:,.2f}")
    print(f"Total gain/loss:    ${total_gain_loss:,.2f}")
    print(f"Total return:        {total_percentage:.2f}%")

    return total_invested, total_market_value


def save_to_csv(portfolio):
    """Save portfolio calculations to a CSV file."""
    fields = [
        "ticker",
        "shares",
        "buy_price",
        "current_price",
        "invested",
        "market_value",
        "gain_loss",
        "percentage",
        "price_source",
        "retrieved_at"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for holding in portfolio:
            writer.writerow({
                "ticker": holding["ticker"],
                "shares": holding["shares"],
                "buy_price": round(holding["buy_price"], 2),
                "current_price": round(holding["current_price"], 2),
                "invested": round(holding["invested"], 2),
                "market_value": round(holding["market_value"], 2),
                "gain_loss": round(holding["gain_loss"], 2),
                "percentage": round(holding["percentage"], 2),
                "price_source": holding["price_source"],
                "retrieved_at": datetime.now().isoformat(
                    timespec="seconds"
                )
            })

    print("\nPortfolio saved to", OUTPUT_FILE)


def main():
    valid_tickers = load_tickers()
    portfolio = []

    while True:
        print("\n===== STOCK PORTFOLIO TRACKER =====")
        print("1. Add stock holding")
        print("2. View portfolio performance")
        print("3. Save summary to CSV")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_holding(portfolio, valid_tickers)

        elif choice == "2":
            if portfolio:
                calculate_portfolio(portfolio)
            else:
                print("Please add a stock holding first.")

        elif choice == "3":
            if portfolio:
                calculate_portfolio(portfolio)
                save_to_csv(portfolio)
            else:
                print("No holdings to save.")

        elif choice == "4":
            print("Thank you for using the tracker!")
            break

        else:
            print("Invalid option. Choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
