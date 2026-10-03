"""Minimal Bot API transport. Tokens and URLs never appear in errors."""
import json
import urllib.error
import urllib.parse
import urllib.request


class TelegramError(Exception):
    def __init__(self, code=0, retry_after=5, reason=''):
        self.code=code
        self.reason=reason
        self.retry_after=max(1,min(int(retry_after),3600))
        super().__init__('Telegram request failed ({}).'.format(code or 'connection'))


class Telegram:
    def __init__(self, token, base='https://api.telegram.org'):
        parsed=urllib.parse.urlsplit(base)
        if base.rstrip('/')!='https://api.telegram.org':
            if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost','::1') or parsed.username or parsed.query or parsed.fragment or parsed.path:
                raise ValueError('Test endpoint must be local HTTP')
            if not token.startswith('test-'):
                raise ValueError('Local test endpoints require a synthetic test- token')
        self.url=base.rstrip('/')+'/bot'+token+'/'
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args,**kwargs): return None
        self.opener=urllib.request.build_opener(NoRedirect)

    def call(self, method, **payload):
        if method not in {'getMe','getWebhookInfo','getUpdates','sendMessage','editMessageText','answerCallbackQuery','setMyCommands'}:
            raise ValueError('Unsupported Telegram method')
        req=urllib.request.Request(self.url+method,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        try:
            with self.opener.open(req,timeout=15) as response:
                body=json.loads(response.read(4*1024*1024))
        except urllib.error.HTTPError as exc:
            try:
                body=json.loads(exc.read(65536))
                delay=body.get('parameters',{}).get('retry_after',5)
                description=str(body.get('description','')).lower()
                reason='unchanged' if 'message is not modified' in description else 'missing' if 'message to edit not found' in description else ''
            except (ValueError,AttributeError,TypeError): delay=5;reason=''
            raise TelegramError(exc.code,delay,reason) from None
        except (OSError,ValueError):
            raise TelegramError() from None
        if not isinstance(body,dict) or body.get('ok') is not True:
            raise TelegramError(body.get('error_code',0) if isinstance(body,dict) else 0)
        return body.get('result')
