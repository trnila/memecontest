#!/usr/bin/env python3
import re
import os
import hmac
import datetime
import json
import hashlib
from quart import Quart, request, send_from_directory
import aioredis

app = Quart(__name__)
app.config.from_pyfile('local_settings.py')

STREAM_CHANNEL = "memestream"
MEMES_PATH = 'memes'

async def get_redis():
    return await aioredis.create_redis_pool(app.config['REDIS_URL'])

async def get_all(redis):
    memes = []
    for f in os.listdir(MEMES_PATH):
        key = f"meme/{f.strip('.png')}"
        path = os.path.join(MEMES_PATH, f)
        updated = os.path.getmtime(path)
        memes.append({
            "path": f'meme/{f}?{updated}',
            "author": f.split('.')[0],
            'liked': [s.decode('utf-8') for s in await redis.smembers(key)],
            'updated': datetime.datetime.fromtimestamp(updated).isoformat(), 
        })
    return memes

@app.route('/meme/<login>.png')
async def meme_get(login):
    return await send_from_directory(MEMES_PATH, f'{login}.png')

@app.route('/meme/<login>.png', methods=['POST'])
async def meme_vote(login):
    def sign(login):
        return hmac.new(app.config['SECRET_KEY'].encode('utf-8'), login.encode('utf-8'), hashlib.sha256).hexdigest()

    token, me = request.headers.get('authorization').split(' ')[1].split('-')
    if not hmac.compare_digest(token, sign(me)):
        return "invalid token", 403

    redis = await get_redis()
    json = await request.get_json()
    
    key = f'meme/{login}'
    if json['like']:
        await redis.sadd(key, me)
    else:
        await redis.srem(key, me)

    await redis.publish_json(STREAM_CHANNEL, await get_all(redis))
    return 'OK'

@app.route('/events')
async def events():
    async def event_stream():
        redis = await get_redis()
        sub = aioredis.pubsub.Receiver()
        await redis.subscribe(sub.channel(STREAM_CHANNEL))
        
        yield f'data: {json.dumps(await get_all(redis))}\n\n'.encode('utf-8')
        async for channel, msg in sub.iter():
            yield b"data: "
            yield msg
            yield b"\n\n"

    return event_stream(), {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Transfer-Encoding': 'chunked',
    }

@app.route('/meme/<login>.png', methods=['PUT'])
async def meme_put(login):
    if not re.match(r'[A-Z]{3}[0-9]{4}$', login) and login != 'student':
        return 'Invalid username', 400

    if request.headers.get('Authorization') != f'Bearer {app.config["SECRET_KEY"]}':
        return 'Invalid token', 403

    with open(os.path.join(MEMES_PATH, f'{login}.png'), 'wb') as f:
        f.write(await request.data)

    redis = await get_redis()
    await redis.publish_json(STREAM_CHANNEL, await get_all(redis))

    return 'Meme uploaded'

@app.route('/')
@app.route('/<path:path>')
async def sstatic(path='index.html'):
    return await send_from_directory('public', path)
