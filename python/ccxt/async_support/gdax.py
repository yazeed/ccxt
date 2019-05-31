# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import base64
import hashlib
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import ArgumentsRequired
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidAddress
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound
from ccxt.base.errors import NotSupported


class gdax (Exchange):

    def describe(self):
        return self.deep_extend(super(gdax, self).describe(), {
            'id': 'gdax',
            'name': 'GDAX',
            'countries': ['US'],
            'rateLimit': 1000,
            'userAgent': self.userAgents['chrome'],
            'has': {
                'cancelAllOrders': True,
                'CORS': True,
                'deposit': True,
                'fetchAccounts': True,
                'fetchClosedOrders': True,
                'fetchDepositAddress': True,
                'createDepositAddress': True,
                'fetchMyTrades': True,
                'fetchOHLCV': True,
                'fetchOpenOrders': True,
                'fetchOrder': True,
                'fetchOrderTrades': True,
                'fetchOrders': True,
                'fetchTransactions': True,
                'withdraw': True,
            },
            'timeframes': {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '1h': 3600,
                '6h': 21600,
                '1d': 86400,
            },
            'urls': {
                'test': 'https://api-public.sandbox.gdax.com',
                'logo': 'https://user-images.githubusercontent.com/1294454/27766527-b1be41c6-5edb-11e7-95f6-5b496c469e2c.jpg',
                'api': 'https://api.gdax.com',
                'www': 'https://www.gdax.com',
                'doc': 'https://docs.gdax.com',
                'fees': [
                    'https://www.gdax.com/fees',
                    'https://support.gdax.com/customer/en/portal/topics/939402-depositing-and-withdrawing-funds/articles',
                ],
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': True,
                'password': True,
            },
            'api': {
                'public': {
                    'get': [
                        'currencies',
                        'products',
                        'products/{id}/book',
                        'products/{id}/candles',
                        'products/{id}/stats',
                        'products/{id}/ticker',
                        'products/{id}/trades',
                        'time',
                    ],
                },
                'private': {
                    'get': [
                        'accounts',
                        'accounts/{id}',
                        'accounts/{id}/holds',
                        'accounts/{id}/ledger',
                        'accounts/{id}/transfers',
                        'coinbase-accounts',
                        'fills',
                        'funding',
                        'orders',
                        'orders/{id}',
                        'otc/orders',
                        'payment-methods',
                        'position',
                        'reports/{id}',
                        'users/self/trailing-volume',
                    ],
                    'post': [
                        'conversions',
                        'deposits/coinbase-account',
                        'deposits/payment-method',
                        'coinbase-accounts/{id}/addresses',
                        'funding/repay',
                        'orders',
                        'position/close',
                        'profiles/margin-transfer',
                        'reports',
                        'withdrawals/coinbase',
                        'withdrawals/crypto',
                        'withdrawals/payment-method',
                    ],
                    'delete': [
                        'orders',
                        'orders/{id}',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': True,  # complicated tier system per coin
                    'percentage': True,
                    'maker': 0.15 / 100,  # highest fee of all tiers
                    'taker': 0.25 / 100,  # highest fee of all tiers
                },
                'funding': {
                    'tierBased': False,
                    'percentage': False,
                    'withdraw': {
                        'BCH': 0,
                        'BTC': 0,
                        'LTC': 0,
                        'ETH': 0,
                        'EUR': 0.15,
                        'USD': 25,
                    },
                    'deposit': {
                        'BCH': 0,
                        'BTC': 0,
                        'LTC': 0,
                        'ETH': 0,
                        'EUR': 0.15,
                        'USD': 10,
                    },
                },
            },
            'exceptions': {
                'exact': {
                    'Insufficient funds': InsufficientFunds,
                    'NotFound': OrderNotFound,
                    'Invalid API Key': AuthenticationError,
                    'invalid signature': AuthenticationError,
                    'Invalid Passphrase': AuthenticationError,
                    'Invalid order id': InvalidOrder,
                },
                'broad': {
                    'Order already done': OrderNotFound,
                    'order not found': OrderNotFound,
                    'price too small': InvalidOrder,
                    'price too precise': InvalidOrder,
                },
            },
        })

    async def fetch_markets(self, params={}):
        response = await self.publicGetProducts(params)
        result = []
        for i in range(0, len(response)):
            market = response[i]
            id = self.safe_string(market, 'id')
            baseId = self.safe_string(market, 'base_currency')
            quoteId = self.safe_string(market, 'quote_currency')
            base = self.common_currency_code(baseId)
            quote = self.common_currency_code(quoteId)
            symbol = base + '/' + quote
            priceLimits = {
                'min': self.safe_float(market, 'quote_increment'),
                'max': None,
            }
            precision = {
                'amount': 8,
                'price': self.precision_from_string(self.safe_string(market, 'quote_increment')),
            }
            taker = self.fees['trading']['taker']  # does not seem right
            if (base == 'ETH') or (base == 'LTC'):
                taker = 0.003
            active = market['status'] == 'online'
            result.append(self.extend(self.fees['trading'], {
                'id': id,
                'symbol': symbol,
                'baseId': baseId,
                'quoteId': quoteId,
                'base': base,
                'quote': quote,
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': self.safe_float(market, 'base_min_size'),
                        'max': self.safe_float(market, 'base_max_size'),
                    },
                    'price': priceLimits,
                    'cost': {
                        'min': self.safe_float(market, 'min_market_funds'),
                        'max': self.safe_float(market, 'max_market_funds'),
                    },
                },
                'taker': taker,
                'active': active,
                'info': market,
            }))
        return result

    async def fetch_accounts(self, params={}):
        response = await self.privateGetAccounts(params)
        #
        #     [
        #         {
        #             id: '4aac9c60-cbda-4396-9da4-4aa71e95fba0',
        #             currency: 'BTC',
        #             balance: '0.0000000000000000',
        #             available: '0',
        #             hold: '0.0000000000000000',
        #             profile_id: 'b709263e-f42a-4c7d-949a-a95c83d065da'
        #         },
        #         {
        #             id: 'f75fa69a-1ad1-4a80-bd61-ee7faa6135a3',
        #             currency: 'USDC',
        #             balance: '0.0000000000000000',
        #             available: '0',
        #             hold: '0.0000000000000000',
        #             profile_id: 'b709263e-f42a-4c7d-949a-a95c83d065da'
        #         },
        #     ]
        #
        result = []
        for i in range(0, len(response)):
            account = response[i]
            accountId = self.safe_string(account, 'id')
            currencyId = self.safe_string(account, 'currency')
            code = self.common_currency_code(currencyId)
            result.append({
                'id': accountId,
                'type': None,
                'currency': code,
                'info': account,
            })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        balances = await self.privateGetAccounts(params)
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            account = {
                'free': self.safe_float(balance, 'available'),
                'used': self.safe_float(balance, 'hold'),
                'total': self.safe_float(balance, 'balance'),
            }
            result[currency] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        orderbook = await self.publicGetProductsIdBook(self.extend({
            'id': self.market_id(symbol),
            'level': 2,  # 1 best bidask, 2 aggregated, 3 full
        }, params))
        return self.parse_order_book(orderbook)

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = self.extend({
            'id': market['id'],
        }, params)
        ticker = await self.publicGetProductsIdTicker(request)
        timestamp = self.parse8601(self.safe_value(ticker, 'time'))
        bid = None
        ask = None
        if 'bid' in ticker:
            bid = self.safe_float(ticker, 'bid')
        if 'ask' in ticker:
            ask = self.safe_float(ticker, 'ask')
        last = self.safe_float(ticker, 'price')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': bid,
            'bidVolume': None,
            'ask': ask,
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'volume'),
            'quoteVolume': None,
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(self.safe_string_2(trade, 'time', 'created_at'))
        symbol = None
        if market is None:
            marketId = self.safe_string(trade, 'product_id')
            market = self.safe_value(self.markets_by_id, marketId)
        if market:
            symbol = market['symbol']
        feeRate = None
        feeCurrency = None
        takerOrMaker = None
        if market is not None:
            feeCurrency = market['quote']
            if 'liquidity' in trade:
                takerOrMaker = 'taker' if (trade['liquidity'] == 'T') else 'maker'
                feeRate = market[takerOrMaker]
        feeCost = self.safe_float(trade, 'fill_fees')
        if feeCost is None:
            feeCost = self.safe_float(trade, 'fee')
        fee = {
            'cost': feeCost,
            'currency': feeCurrency,
            'rate': feeRate,
        }
        type = None
        id = self.safe_string(trade, 'trade_id')
        side = 'sell' if (trade['side'] == 'buy') else 'buy'
        orderId = self.safe_string(trade, 'order_id')
        # GDAX returns inverted side to fetchMyTrades vs fetchTrades
        if orderId is not None:
            side = 'buy' if (trade['side'] == 'buy') else 'sell'
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'size')
        return {
            'id': id,
            'order': orderId,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': type,
            'takerOrMaker': takerOrMaker,
            'side': side,
            'price': price,
            'amount': amount,
            'fee': fee,
            'cost': price * amount,
        }

    async def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        # as of 2018-08-23
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchMyTrades requires a symbol argument')
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'product_id': market['id'],
        }
        if limit is not None:
            request['limit'] = limit
        response = await self.privateGetFills(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetProductsIdTrades(self.extend({
            'id': market['id'],  # fixes issue  #2
        }, params))
        return self.parse_trades(response, market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv[0] * 1000,
            ohlcv[3],
            ohlcv[2],
            ohlcv[1],
            ohlcv[4],
            ohlcv[5],
        ]

    async def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        granularity = self.timeframes[timeframe]
        request = {
            'id': market['id'],
            'granularity': granularity,
        }
        if since is not None:
            request['start'] = self.ymdhms(since)
            if limit is None:
                # https://docs.gdax.com/#get-historic-rates
                limit = 300  # max = 300
            request['end'] = self.ymdhms(self.sum(limit * granularity * 1000, since))
        response = await self.publicGetProductsIdCandles(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    async def fetch_time(self, params={}):
        response = await self.publicGetTime(params)
        return self.parse8601(self.parse8601(response, 'iso'))

    def parse_order_status(self, status):
        statuses = {
            'pending': 'open',
            'active': 'open',
            'open': 'open',
            'done': 'closed',
            'canceled': 'canceled',
            'canceling': 'open',
        }
        return self.safe_string(statuses, status, status)

    def parse_order(self, order, market=None):
        timestamp = self.parse8601(order['created_at'])
        symbol = None
        if market is None:
            if order['product_id'] in self.markets_by_id:
                market = self.markets_by_id[order['product_id']]
        status = self.parse_order_status(self.safe_string(order, 'status'))
        price = self.safe_float(order, 'price')
        amount = self.safe_float(order, 'size')
        if amount is None:
            amount = self.safe_float(order, 'funds')
        if amount is None:
            amount = self.safe_float(order, 'specified_funds')
        filled = self.safe_float(order, 'filled_size')
        remaining = None
        if amount is not None:
            if filled is not None:
                remaining = amount - filled
        cost = self.safe_float(order, 'executed_value')
        fee = {
            'cost': self.safe_float(order, 'fill_fees'),
            'currency': None,
            'rate': None,
        }
        if market:
            symbol = market['symbol']
        return {
            'id': order['id'],
            'info': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': order['type'],
            'side': order['side'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'fee': fee,
        }

    async def fetch_order(self, id, symbol=None, params={}):
        await self.load_markets()
        response = await self.privateGetOrdersId(self.extend({
            'id': id,
        }, params))
        return self.parse_order(response)

    async def fetch_order_trades(self, id, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        request = {
            'order_id': id,
        }
        response = await self.privateGetFills(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    async def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        request = {
            'status': 'all',
        }
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['product_id'] = market['id']
        response = await self.privateGetOrders(self.extend(request, params))
        return self.parse_orders(response, market, since, limit)

    async def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        request = {}
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['product_id'] = market['id']
        response = await self.privateGetOrders(self.extend(request, params))
        return self.parse_orders(response, market, since, limit)

    async def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        request = {
            'status': 'done',
        }
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['product_id'] = market['id']
        response = await self.privateGetOrders(self.extend(request, params))
        return self.parse_orders(response, market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        # oid = str(self.nonce())
        request = {
            'product_id': self.market_id(symbol),
            'side': side,
            'size': self.amount_to_precision(symbol, amount),
            'type': type,
        }
        if type == 'limit':
            request['price'] = self.price_to_precision(symbol, price)
        response = await self.privatePostOrders(self.extend(request, params))
        return self.parse_order(response)

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        return await self.privateDeleteOrdersId({'id': id})

    async def cancel_all_orders(self, symbol=None, params={}):
        return await self.privateDeleteOrders(params)

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={}):
        market = self.markets[symbol]
        rate = market[takerOrMaker]
        cost = amount * price
        currency = market['quote']
        return {
            'type': takerOrMaker,
            'currency': currency,
            'rate': rate,
            'cost': float(self.currency_to_precision(currency, rate * cost)),
        }

    async def get_payment_methods(self):
        response = await self.privateGetPaymentMethods()
        return response

    async def deposit(self, code, amount, address, params={}):
        await self.load_markets()
        currency = self.currency(code)
        request = {
            'currency': currency['id'],
            'amount': amount,
        }
        method = 'privatePostDeposits'
        if 'payment_method_id' in params:
            # deposit from a payment_method, like a bank account
            method += 'PaymentMethod'
        elif 'coinbase_account_id' in params:
            # deposit into GDAX account from a Coinbase account
            method += 'CoinbaseAccount'
        else:
            # deposit methodotherwise we did not receive a supported deposit location
            # relevant docs link for the Googlers
            # https://docs.gdax.com/#deposits
            raise NotSupported(self.id + ' deposit() requires one of `coinbase_account_id` or `payment_method_id` extra params')
        response = await getattr(self, method)(self.extend(request, params))
        if not response:
            raise ExchangeError(self.id + ' deposit() error: ' + self.json(response))
        return {
            'info': response,
            'id': response['id'],
        }

    async def withdraw(self, code, amount, address, tag=None, params={}):
        self.check_address(address)
        currency = self.currency(code)
        await self.load_markets()
        request = {
            'currency': currency['id'],
            'amount': amount,
        }
        method = 'privatePostWithdrawals'
        if 'payment_method_id' in params:
            method += 'PaymentMethod'
        elif 'coinbase_account_id' in params:
            method += 'CoinbaseAccount'
        else:
            method += 'Crypto'
            request['crypto_address'] = address
        response = await getattr(self, method)(self.extend(request, params))
        if not response:
            raise ExchangeError(self.id + ' withdraw() error: ' + self.json(response))
        return {
            'info': response,
            'id': response['id'],
        }

    async def fetch_transactions(self, code=None, since=None, limit=None, params={}):
        await self.load_markets()
        await self.loadAccounts()
        currency = None
        id = self.safe_string(params, 'id')  # account id
        if id is None:
            if code is None:
                raise ArgumentsRequired(self.id + ' fetchTransactions() requires a currency code argument if no account id specified in params')
            currency = self.currency(code)
            accountsByCurrencyCode = self.index_by(self.accounts, 'currency')
            account = self.safe_value(accountsByCurrencyCode, code)
            if account is None:
                raise ExchangeError(self.id + ' fetchTransactions() could not find account id for ' + code)
            id = account['id']
        request = {
            'id': id,
        }
        if limit is not None:
            request['limit'] = limit
        response = await self.privateGetAccountsIdTransfers(self.extend(request, params))
        for i in range(0, len(response)):
            response[i]['currency'] = code
        return self.parseTransactions(response, currency, since, limit)

    def parse_transaction_status(self, transaction):
        canceled = self.safe_value(transaction, 'canceled_at')
        if canceled:
            return 'canceled'
        processed = self.safe_value(transaction, 'processed_at')
        completed = self.safe_value(transaction, 'completed_at')
        if processed and completed:
            return 'ok'
        elif processed and not completed:
            return 'failed'
        else:
            return 'pending'

    def parse_transaction(self, transaction, currency=None):
        details = self.safe_value(transaction, 'details', {})
        id = self.safe_string(transaction, 'id')
        txid = self.safe_string(details, 'crypto_transaction_hash')
        timestamp = self.parse8601(self.safe_string(transaction, 'created_at'))
        updated = self.parse8601(self.safe_string(transaction, 'processed_at'))
        code = None
        currencyId = self.safe_string(transaction, 'currency')
        if currencyId in self.currencies_by_id:
            currency = self.currencies_by_id[currencyId]
            code = currency['code']
        else:
            code = self.common_currency_code(currencyId)
        fee = None
        status = self.parse_transaction_status(transaction)
        amount = self.safe_float(transaction, 'amount')
        type = self.safe_string(transaction, 'type')
        address = self.safe_string(details, 'crypto_address')
        tag = self.safe_string(details, 'destination_tag')
        address = self.safe_string(transaction, 'crypto_address', address)
        if type == 'withdraw':
            type = 'withdrawal'
            address = self.safe_string(details, 'sent_to_address', address)
        return {
            'info': transaction,
            'id': id,
            'txid': txid,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'address': address,
            'tag': tag,
            'type': type,
            'amount': amount,
            'currency': code,
            'status': status,
            'updated': updated,
            'fee': fee,
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if method == 'GET':
            if query:
                request += '?' + self.urlencode(query)
        url = self.urls['api'] + request
        if api == 'private':
            self.check_required_credentials()
            nonce = str(self.nonce())
            payload = ''
            if method != 'GET':
                if query:
                    body = self.json(query)
                    payload = body
            # payload = body if (body) else ''
            what = nonce + method + request + payload
            secret = base64.b64decode(self.secret)
            signature = self.hmac(self.encode(what), secret, hashlib.sha256, 'base64')
            headers = {
                'CB-ACCESS-KEY': self.apiKey,
                'CB-ACCESS-SIGN': self.decode(signature),
                'CB-ACCESS-TIMESTAMP': nonce,
                'CB-ACCESS-PASSPHRASE': self.password,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def fetch_deposit_address(self, code, params={}):
        await self.load_markets()
        currency = self.currency(code)
        accounts = self.safe_value(self.options, 'coinbaseAccounts')
        if accounts is None:
            accounts = await self.privateGetCoinbaseAccounts()
            self.options['coinbaseAccounts'] = accounts  # cache it
            self.options['coinbaseAccountsByCurrencyId'] = self.index_by(accounts, 'currency')
        currencyId = currency['id']
        account = self.safe_value(self.options['coinbaseAccountsByCurrencyId'], currencyId)
        if account is None:
            # eslint-disable-next-line quotes
            raise InvalidAddress(self.id + " fetchDepositAddress() could not find currency code " + code + " with id = " + currencyId + " in self.options['coinbaseAccountsByCurrencyId']")
        request = {
            'id': account['id'],
        }
        response = await self.privateGetCoinbaseAccountsIdAddresses(self.extend(request, params))
        address = self.safe_string(response, 'address')
        tag = self.safe_string(response, 'destination_tag')
        return {
            'currency': code,
            'address': self.check_address(address),
            'tag': tag,
            'info': response,
        }

    async def create_deposit_address(self, code, params={}):
        await self.load_markets()
        currency = self.currency(code)
        accounts = self.safe_value(self.options, 'coinbaseAccounts')
        if accounts is None:
            accounts = await self.privateGetCoinbaseAccounts()
            self.options['coinbaseAccounts'] = accounts  # cache it
            self.options['coinbaseAccountsByCurrencyId'] = self.index_by(accounts, 'currency')
        currencyId = currency['id']
        account = self.safe_value(self.options['coinbaseAccountsByCurrencyId'], currencyId)
        if account is None:
            # eslint-disable-next-line quotes
            raise InvalidAddress(self.id + " fetchDepositAddress() could not find currency code " + code + " with id = " + currencyId + " in self.options['coinbaseAccountsByCurrencyId']")
        request = {
            'id': account['id'],
        }
        response = await self.privatePostCoinbaseAccountsIdAddresses(self.extend(request, params))
        address = self.safe_string(response, 'address')
        tag = self.safe_string(response, 'destination_tag')
        return {
            'currency': code,
            'address': self.check_address(address),
            'tag': tag,
            'info': response,
        }

    def handle_errors(self, code, reason, url, method, headers, body, response):
        if (code == 400) or (code == 404):
            if body[0] == '{':
                message = response['message']
                feedback = self.id + ' ' + message
                exact = self.exceptions['exact']
                if message in exact:
                    raise exact[message](feedback)
                broad = self.exceptions['broad']
                broadKey = self.findBroadlyMatchedKey(broad, message)
                if broadKey is not None:
                    raise broad[broadKey](feedback)
                raise ExchangeError(feedback)  # unknown message
            raise ExchangeError(self.id + ' ' + body)

    async def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = await self.fetch2(path, api, method, params, headers, body)
        if 'message' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response
