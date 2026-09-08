export { Room } from './room.js';

// 只有一個房間，名字固定。要開第二場就換這個字串。
const ROOM_NAME = 'likai-0909';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith('/api')) {
      const id = env.ROOM.idFromName(ROOM_NAME);
      return env.ROOM.get(id).fetch(request);
    }
    return env.ASSETS.fetch(request);
  },
};
