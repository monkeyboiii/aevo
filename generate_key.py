import asyncio
from aevo import AevoClient
import argparse
from eth_account import Account
from jproperties import Properties


configs = Properties()


async def main(args):
    if args.file is None:
        print('file not suppiled')
        exit(-1)

    with open(args.file, 'rb') as file:
        configs.load(file)

    acc = Account.from_key(configs.get('PRIVATE_KEY').data)
    aevo = AevoClient(
        signing_key=configs.get('SIGNING_KEY').data,
        wallet_address=acc.address,
        api_key=configs.get('API_KEY').data,
        api_secret=configs.get('API_SECRET').data,
        env="testnet",
    )

    print(aevo.get_markets('BTC'))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()  
    parser.add_argument('-f', '--file', required=False)
    args = parser.parse_args()
    
    asyncio.run(main(args))
