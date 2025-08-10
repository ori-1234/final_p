# back/init_orchestrator.py
import os
import sys
import django
import logging
import argparse
from datetime import timedelta
from django.utils import timezone
from django.core.management import call_command

# --- Django Setup ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
# --- End Django Setup ---

from analytics.models import Coin, MarketData
from django.contrib.auth import get_user_model

# Analytics tasks/helpers (נשתמש בפונקציות הקיימות כדי לא לכפול קוד)
from analytics.tasks import (
    fetch_binance_candles,
    BinanceInterval,
    calculate_technical_indicators,
    process_and_save_data,
    update_all_coin_details,
    fetch_news_sentiment_data,
)

# Analysis tasks (חישוב פיצ'רים טכניים וסנטימנט)
from analysis.tasks import (
    update_all_technical_features_for_symbol,
    update_all_sentiment_features_for_symbol,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_COINS = ['BTC', 'ETH', 'SOL', 'XRP', 'LTC']


def apply_migrations():
    logger.info("Applying migrations...")
    call_command('migrate', interactive=False)
    logger.info("Migrations applied.")


def seed_coins():
    logger.info("Seeding coins...")
    coins = [
        ('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('SOL', 'Solana'),
        ('XRP', 'XRP'), ('LTC', 'Litecoin'), ('USDC', 'USD Coin'), ('USD', 'US Dollar'),
    ]
    created = 0
    for sym, name in coins:
        _, was_created = Coin.objects.get_or_create(symbol=sym, defaults={'name': name})
        created += int(was_created)
    logger.info(f"Seeded coins. New created: {created}")


def seed_detailed_coins(use_given_ids: bool = False):
    """
    יוצר/מעדכן מטבעות עם נתוני תיאור, לוגו ופעיל.
    אם use_given_ids=True ו-id קיים – מנסה לשמור את ה-id הנתון עבור רשומות חדשות.
    """
    coins = [
        {
            "id": 1,
            "symbol": "BTC",
            "name": "Bitcoin",
            "description": "Bitcoin is the first successful internet money based on peer-to-peer technology, whereby no central bank or authority is involved in the transaction and production of the Bitcoin currency. It was created by an anonymous individual/group under the name, Satoshi Nakamoto. The source code is available publicly as an open source project, anybody can look at it and be part of the developmental process. Bitcoin is changing the way we see money as we speak. The idea was to produce a means of exchange, independent of any central authority, that could be transferred electronically in a secure, verifiable and immutable way. It is a decentralized peer-to-peer internet currency making mobile payment easy, very low transaction fees, protects your identity, and it works anywhere all the time with no central authority and banks. Bitcoin is designed to have only 21 million BTC ever created, thus making it a deflationary currency. Bitcoin uses the SHA-256 hashing algorithm with an average transaction confirmation time of 10 minutes. Miners today are mining Bitcoin using ASIC chip dedicated to only mining Bitcoin, and the hash rate has shot up to peta hashes. Being the first successful online cryptography currency, Bitcoin has inspired other alternative currencies such as Litecoin, Peercoin, Primecoin, and so on. The cryptocurrency then took off with the innovation of the turing-complete smart contract by Ethereum which led to the development of other amazing projects such as EOS, Tron, and even crypto-collectibles such as CryptoKitties.",
            "image_url": "https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png?1696501400",
            "active": True
        },
        {
            "id": 2,
            "symbol": "ETH",
            "name": "Ethereum",
            "description": "Ethereum is a global, open-source platform for decentralized applications. In other words, the vision is to create a world computer that anyone can build applications in a decentralized manner; while all states and data are distributed and publicly accessible. Ethereum supports smart contracts in which developers can write code in order to program digital value. Examples of decentralized apps (dapps) that are built on Ethereum includes tokens, non-fungible tokens, decentralized finance apps, lending protocol, decentralized exchanges, and much more. On Ethereum, all transactions and smart contract executions require a small fee to be paid. This fee is called Gas. In technical terms, Gas refers to the unit of measure on the amount of computational effort required to execute an operation or a smart contract. The more complex the execution operation is, the more gas is required to fulfill that operation. Gas fees are paid entirely in Ether (ETH), which is the native coin of the blockchain. The price of gas can fluctuate from time to time depending on the network demand.",
            "image_url": "https://coin-images.coingecko.com/coins/images/279/large/ethereum.png?1696501628",
            "active": True
        },
        {
            "id": 3,
            "symbol": "SOL",
            "name": "Solana",
            "description": "Solana is a highly functional open source project that banks on blockchain technology’s permissionless nature to provide decentralized finance (DeFi) solutions. It is a layer 1 network that offers fast speeds and affordable costs. While the idea and initial work on the project began in 2017, Solana was officially launched in March 2020 by the Solana Foundation with headquarters in Geneva, Switzerland.",
            "image_url": "https://coin-images.coingecko.com/coins/images/4128/large/solana.png?1718769756",
            "active": True
        },
        {
            "id": 4,
            "symbol": "XRP",
            "name": "XRP",
            "description": "Ripple is the catchall name for the cryptocurrency platform, the transactional protocol for which is actually XRP, in the same fashion as Ethereum is the name for the platform that facilitates trades in Ether. Like other cryptocurrencies, Ripple is built atop the idea of a distributed ledger network which requires various parties to participate in validating transactions, rather than any singular centralized authority. That facilitates transactions all over the world, and transfer fees are far cheaper than the likes of bitcoin. Unlike other cryptocurrencies, XRP transfers are effectively immediate, requiring no typical confirmation time. Ripple was originally founded by a single company, Ripple Labs, and continues to be backed by it, rather than the larger network of developers that continue bitcoin’s development. It also doesn’t have a fluctuating amount of its currency in existence. Where bitcoin has a continually growing pool with an eventual maximum, and Ethereum theoretically has no limit, Ripple was created with all of its 100 billion XRP tokens right out of the gate. That number is maintained with no mining and most of the tokens are owned and held by Ripple Labs itself — around 60 billion at the latest count. Even at the recently reduced value of around half a dollar per XRP, that means Ripple Labs is currently sitting on around $20 billion worth of the cryptocurrency (note: Ripple’s price crashed hard recently, and may be worth far less than $60 billion by time you read this). It holds 55 billion XRP in an escrow account, which allows it to sell up to a billion per month if it so chooses in order to fund new projects and acquisitions. Selling such an amount would likely have a drastic effect on the cryptocurrency’s value, and isn’t something Ripple Labs plans to do anytime soon. In actuality, Ripple Labs is looking to leverage the technology behind XRP to allow for faster banking transactions around the world. While Bitcoin and other cryptocurrencies are built on the idea of separating financial transactions from the financial organizations of traditional currencies, Ripple is almost the opposite in every sense. XRP by Ripple price can be found on this page alongside the market capitalization and additional stats.",
            "image_url": "https://coin-images.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png?1696501442",
            "active": True
        },
        {
            "id": 6,
            "symbol": "LTC",
            "name": "Litecoin",
            "description": "Litecoin is a peer-to-peer cryptocurrency created by Charlie Lee. It was created based on the Bitcoin protocol but differs in terms of the hashing algorithm used. Litecoin uses the memory intensive Scrypt proof of work mining algorithm. Scrypt allows consumer-grade hardware such as GPU to mine those coins. Why Litecoin? Litecoin is a cryptocurrency that has evolved from Bitcoin after its own popularity in the industry, this alternative, or ‘altcoin’ has emerged to allow investors to diversify their digital currency package, according to Investopedia. Litecoin is one of the most prominent altcoins and was created by former Google employee and Director of Engineering at Coinbase, Charlie Lee. Litecoin was the first to alter Bitcoin and the most significant difference is that it takes 2.5 minutes for Litecoin to generate a block, or transaction, in comparison to Bitcoin`s 10 minutes. ‘While this matters little to traders, miners who use hardware to run Bitcoin`s network cannot switch over to Litecoin. This keeps bigger mining conglomerates away from Litecoin because they cannot easily optimize their profits by swapping to another coin, contributing to a more decentralized experience. Litecoin also has bigger blocks, and more coins in circulation, making it more affordable and swift when transacting,’ Investopedia explained. As explained above, Litecoin can transact a lot faster than Bitcoin, but there are also a number of other characteristics that investors need to know before trading. Litecoin can handle higher volumes of transactions because of the capability of transacting faster and if Bitcoin attempted to transact on the scale of its altcoin, a code update would be needed. However, Litecoin’s blocks would be larger, but with more `orphaned blocks`. The faster block time of litecoin reduces the risk of double spending attacks - this is theoretical in the case of both networks having the same hashing power. Litecoin Technical Details: The transaction confirmation time taken for Litecoin is about 2.5 minutes on average (as compared to Bitcoin`s 10 minutes). The Litecoin network is scheduled to cap at 84 million currency units. Litecoin has inspired many other popular alternative currencies (eg. Dogecoin) because of its Scrypt hashing algorithm in order to prevent ASIC miners from mining those coins. However it is said that by the end of this year, Scrypt ASIC will enter the mass market.",
            "image_url": "https://coin-images.coingecko.com/coins/images/2/large/litecoin.png?1696501400",
            "active": True
        }
    ]

    created, updated = 0, 0
    for c in coins:
        sym = c["symbol"].upper()
        defaults = {
            "name": c["name"],
            "description": c.get("description") or "",
            "logo": c.get("image_url"),
            "is_active": bool(c.get("active", True)),
        }
        obj = Coin.objects.filter(symbol=sym).first()
        if obj:
            for k, v in defaults.items():
                setattr(obj, k, v)
            obj.save()
            updated += 1
        else:
            data = {"symbol": sym, **defaults}
            if use_given_ids and "id" in c:
                data["id"] = c["id"]
            Coin.objects.create(**data)
            created += 1
    logger.info(f"Seeded detailed coins. Created: {created}, Updated: {updated}")

def ensure_superuser(username: str | None = None, email: str | None = None, password: str | None = None):
    """
    Creates a Django superuser using ENV overrides when provided.
    ENV vars:
      - ADMIN_USERNAME (default: 'admin')
      - ADMIN_EMAIL (default: 'admin@example.com')
      - ADMIN_PASSWORD (default: 'admin')
    """
    username = username or os.environ.get('ADMIN_USERNAME', 'admin')
    email = email or os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    password = password or os.environ.get('ADMIN_PASSWORD', 'admin')

    User = get_user_model()
    if not User.objects.filter(username=username).exists():
        logger.info(f"Creating superuser {username} ...")
        User.objects.create_superuser(username=username, email=email, password=password)
        logger.info("Superuser created.")
    else:
        logger.info("Superuser already exists; skipping.")


def deep_backfill_market_data(coins, days=456):
    """
    Backfill היסטוריה ברמת 12h ל ~1.25 שנים (ברירת מחדל), כולל חישוב אינדיקטורים ושמירה ל-DB.
    דומה ל-back/analytics/test.py אבל משתמש ב-helpers מתוך analytics.tasks.
    """
    end_time = timezone.now()
    start_time = end_time - timedelta(days=days)
    logger.info(f"Deep backfill {days}d (12h candles) from {start_time} to {end_time}")

    for symbol in coins:
        try:
            logger.info(f"[{symbol}] downloading candles ...")
            df = fetch_binance_candles(symbol, BinanceInterval.HOUR_12, start_time, end_time)
            if df is None or df.empty:
                logger.warning(f"[{symbol}] no data returned; skipping.")
                continue

            # חישובי אינדיקטורים
            df = calculate_technical_indicators(df)

            # 24h change על בסיס נרות 12h (2 תקופות אחורה)
            import pandas as pd
            df['price_change_percent_24h'] = (df['close_price'].pct_change(periods=2) * 100)

            # שמירה ל-DB (כולל אינדיקטורים)
            ok = process_and_save_data(symbol, df)
            if ok:
                logger.info(f"[{symbol}] saved {len(df)} rows (includes indicators).")
        except Exception as e:
            logger.error(f"[{symbol}] deep backfill error: {e}", exc_info=True)


def compute_technical_features_for_all(coins):
    logger.info("Computing technical features for all coins...")
    total = 0
    for symbol in coins:
        try:
            res = update_all_technical_features_for_symbol(symbol)
            logger.info(f"[{symbol}] technical features: {res}")
            total += 1
        except Exception as e:
            logger.error(f"[{symbol}] technical features error: {e}", exc_info=True)
    logger.info(f"Finished technical features for {total} coins.")


def compute_sentiment_features_for_all(coins):
    """
    מצפה שיש נתוני DailySentimentData ב-DB. אם אין, ניתן לנסות להפעיל fetch_news_sentiment_data קודם.
    """
    logger.info("Computing sentiment features for all coins...")
    total = 0
    for symbol in coins:
        try:
            res = update_all_sentiment_features_for_symbol(symbol)
            logger.info(f"[{symbol}] sentiment features: {res}")
            total += 1
        except Exception as e:
            logger.error(f"[{symbol}] sentiment features error: {e}", exc_info=True)
    logger.info(f"Finished sentiment features for {total} coins.")


def warm_all_caches(coins):
    logger.info("Warming chart/volume caches for all coins...")
    try:
        update_all_coin_details()
        logger.info("Caches warmed.")
    except Exception as e:
        logger.error(f"Cache warm error: {e}", exc_info=True)


def trigger_n8n_sentiment(coins):
    """
    שולח Webhook ל-n8n (לפי N8N_SENTIMENT_ANALYSIS_URL). 
    ה-flow ב-n8n אמור לשמור חדשות/סנטימנט ל-DB (DailySentimentData/NewsSentimentData).
    """
    logger.info("Triggering n8n sentiment fetch...")
    for s in coins:
        try:
            fetch_news_sentiment_data.delay(s)  # נשתמש ב-celery אם הרץ קיים; אחרת אפשר לקרוא ישירות
            logger.info(f"[{s}] n8n webhook dispatched.")
        except Exception as e:
            logger.error(f"[{s}] n8n webhook error: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Project initialization orchestrator")
    parser.add_argument("--coins", nargs="*", default=DEFAULT_COINS, help="Symbols to process")
    parser.add_argument("--migrate", action="store_true")
    parser.add_argument("--seed-coins", action="store_true")
    parser.add_argument("--seed-detailed-coins", action="store_true")
    parser.add_argument("--use-given-ids", action="store_true")
    parser.add_argument("--superuser", action="store_true", help="Create default admin/admin")
    parser.add_argument("--deep-backfill-days", type=int, default=0, help="If >0, run deep backfill for N days (12h candles)")
    parser.add_argument("--compute-tech", action="store_true")
    parser.add_argument("--compute-sent", action="store_true")
    parser.add_argument("--warm-caches", action="store_true")
    parser.add_argument("--fetch-sentiment-n8n", action="store_true", help="Trigger n8n sentiment webhook (requires n8n up)")
    parser.add_argument("--all", action="store_true", help="Run full flow: migrate, seed, deep backfill (456d), compute tech, warm caches")

    args = parser.parse_args()
    coins = [c.upper() for c in args.coins]

    if args.all:
        apply_migrations()
        seed_coins()
        ensure_superuser()
        days = args.deep_backfill_days if args.deep_backfill_days > 0 else 456
        deep_backfill_market_data(coins, days=days)
        compute_technical_features_for_all(coins)
        warm_all_caches(coins)
        # שלב סנטימנט אופציונלי, כי תלוי ב-n8n/DB:
        # trigger_n8n_sentiment(coins)
        # compute_sentiment_features_for_all(coins)
        return

    if args.migrate:
        apply_migrations()
    if args.seed_coins:
        seed_coins()
    if args.seed_detailed_coins:
        seed_detailed_coins(use_given_ids=args.use_given_ids)
    if args.superuser:
        ensure_superuser()

    if args.deep_backfill_days and args.deep_backfill_days > 0:
        deep_backfill_market_data(coins, days=args.deep_backfill_days)

    if args.compute_tech:
        compute_technical_features_for_all(coins)

    if args.fetch_sentiment_n8n:
        trigger_n8n_sentiment(coins)

    if args.compute_sent:
        compute_sentiment_features_for_all(coins)

    if args.warm_caches:
        warm_all_caches(coins)


if __name__ == "__main__":
    main()