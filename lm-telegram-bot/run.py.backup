"""Start the simple Lords Tracker bot. Python standard library only."""
import argparse
import contextlib
import getpass
import json
import os
from pathlib import Path
import re
import sys
import time
from bot import Bot
from data import Store
from telegram import Telegram, TelegramError


class RunLock:
    def __init__(self,path): self.path=path;self.file=None
    def __enter__(self):
        self.file=self.path.open('a+b')
        self.file.seek(0);self.file.write(b'0');self.file.flush();self.file.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            self.file.close()
            raise RuntimeError('The bot is already running. Close its other window first.') from None
        return self
    def __exit__(self,*args):
        self.file.close()


def save_config(path, data):
    temp=path.with_suffix('.tmp')
    fd=os.open(str(temp),os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as stream: json.dump(data,stream)
    os.replace(temp,path)
    try: path.chmod(0o600)
    except OSError: pass


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',type=Path,default=Path(__file__).resolve().parent.parent/'runs')
    parser.add_argument('--setup',action='store_true',help='Replace the locally saved Telegram bot token')
    args=parser.parse_args(argv)
    state=args.runs/'telegram';state.mkdir(parents=True,exist_ok=True)
    try:
        with RunLock(state/'bot.lock'):
            config_path=state/'config.json'
            config=json.loads(config_path.read_text()) if config_path.exists() and not args.setup else {}
            token=os.environ.get('TELEGRAM_BOT_TOKEN') or config.get('token')
            new_token=False
            if not token:
                print('First-time setup: create your bot with @BotFather using /newbot.')
                print('Paste the Telegram bot token below. Keep it private; input is hidden.')
                token=getpass.getpass('Bot token: ').strip();new_token=True
            if not re.fullmatch(r'[0-9]+:[A-Za-z0-9_-]{20,}',token):
                raise RuntimeError('That is not a Telegram bot token. Get the token from @BotFather.')
            api=Telegram(token)
            me=api.call('getMe')
            webhook=api.call('getWebhookInfo')
            if webhook and webhook.get('url'):
                raise RuntimeError('This bot uses a webhook elsewhere. Use a new @BotFather bot for this app.')
            if new_token:save_config(config_path,{'token':token})
            store=Store(state/'tracker.sqlite3')
            try:
                old_bot=store.setting('bot_id')
                if old_bot is not None and old_bot!=me['id']:
                    with store.db:
                        store.db.execute('DELETE FROM settings')
                        store.db.execute('DELETE FROM follows')
                        store.db.execute('DELETE FROM alerts')
                store.set_setting('bot_id',me['id'])
                bot=Bot(store,api)
                api.call('setMyCommands',commands=[{'command':'menu','description':'Open the tracker menu'}])
                print('\nLords Tracker is running. Keep this window open.')
                if bot.owner() is None:
                    print('Connect your Telegram account by opening this private link:')
                    print('https://t.me/{}?start={}'.format(me['username'],bot.pair_code))
                else: print('Open @{} in Telegram and send /menu.'.format(me['username']))
                print('Saved game observations load automatically. Ctrl+C stops the bot.\n')
                offset=store.setting('telegram_offset',0)
                while True:
                    try:
                        store.sync(args.runs)
                        bot.alerts()
                        updates=api.call('getUpdates',offset=offset,timeout=1,
                                         allowed_updates=['message','callback_query']) or []
                        for update in updates:
                            bot.handle(update)
                            offset=update['update_id']+1
                            store.set_setting('telegram_offset',offset)
                    except TelegramError as exc:
                        if exc.code in (401,409):
                            raise RuntimeError('Telegram rejected the session. Check the bot token or close another running copy.') from None
                        print('Telegram connection paused. Retrying in {} seconds.'.format(exc.retry_after),flush=True)
                        time.sleep(exc.retry_after)
            finally:
                store.db.close()
    except KeyboardInterrupt:
        print('\nBot stopped. Saved players and follows are kept.')
        return 0
    except TelegramError as exc:
        print('Could not connect to Telegram ({}). Check your token and internet connection.'.format(exc.code or 'network'),file=sys.stderr)
        return 2
    except (OSError,ValueError,RuntimeError) as exc:
        # Never print raw URLs or secrets from transport exceptions.
        print('Setup problem: {}'.format(exc),file=sys.stderr)
        return 2
    return 0


if __name__=='__main__': raise SystemExit(main())
