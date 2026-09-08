// 一個房間 = 一個 Durable Object。
// DO 對同一個物件的請求是序列化執行的，所以五個人同時投票不會互相蓋掉——
// 這是選 DO 而不是 KV 的唯一理由，也是最重要的理由。

const EMPTY = () => ({ state: null, seats: {}, votes: {} });

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
    },
  });

export class Room {
  constructor(ctx) {
    this.ctx = ctx;
  }

  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\/api\/?/, '');
    const store = this.ctx.storage;

    if (request.method === 'GET') {
      return json((await store.get('room')) || EMPTY());
    }

    if (request.method !== 'POST') {
      return json({ error: 'method' }, 405);
    }

    const body = await request.json().catch(() => ({}));
    const room = (await store.get('room')) || EMPTY();

    switch (path) {
      case 'state':
        room.state = body.state;
        break;

      case 'seat': {
        // 先搶先贏。已經有人坐了就回 ok:false，前端不會把 me 設進去。
        if (room.seats[body.role]) {
          return json({ ok: false, taken: true, room });
        }
        room.seats[body.role] = { at: Date.now() };
        break;
      }

      case 'vote':
        if (!body.key) return json({ error: 'key' }, 400);
        room.votes[body.key] = { choice: body.choice, at: Date.now() };
        break;

      case 'reset':
        room.state = body.state || null;
        room.seats = {};
        room.votes = {};
        break;

      default:
        return json({ error: 'path' }, 404);
    }

    await store.put('room', room);
    return json({ ok: true, room });
  }
}
