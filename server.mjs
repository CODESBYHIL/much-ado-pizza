// Serves the site and takes payment with Stripe's embedded checkout, so visitors never leave the page.
// No packages needed. Prices come from menu.json (written by build.py), never from the browser.
//
//   STRIPE_SECRET_KEY=sk_test_... STRIPE_PUBLISHABLE_KEY=pk_test_... node server.mjs
//   then open http://localhost:4242
//
// Without the keys it still serves the site, and the bag runs in demo mode. Paid orders are appended to
// orders.jsonl; in production, point a Stripe webhook (checkout.session.completed) at the kitchen instead.
import { createServer } from 'node:http';
import { appendFile, readFile } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('.', import.meta.url));
const PORT = Number(process.env.PORT) || 4242;
const SK = process.env.STRIPE_SECRET_KEY, PK = process.env.STRIPE_PUBLISHABLE_KEY;
const MENU = JSON.parse(await readFile(join(ROOT, 'menu.json'), 'utf8'));
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.mp4': 'video/mp4', '.svg': 'image/svg+xml' };
const recorded = new Set();

const stripe = async (path, params, method = 'POST') => {
  const r = await fetch('https://api.stripe.com/v1/' + path, { method,
    headers: { Authorization: `Bearer ${SK}`, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: method === 'POST' ? new URLSearchParams(params) : undefined });
  const j = await r.json();
  if (!r.ok) throw new Error(j.error?.message || 'Stripe error');
  return j;
};

// checks one bag line against the menu; returns a Stripe line item or throws
const line = (l) => {
  const it = MENU[l?.id], o = l?.opts || {};
  if (!it?.cents) throw new Error('Unknown item');
  if (!Number.isInteger(l.qty) || l.qty < 1 || l.qty > 20) throw new Error('Bad quantity');
  for (const k of ['style', 'sauce', 'dip']) if (o[k] !== undefined && !it.opts[k]?.includes(o[k])) throw new Error(`Bad ${k}`);
  if (o.toppings !== undefined && (!Array.isArray(o.toppings) || o.toppings.length > 5 || !o.toppings.every((t) => it.opts.toppings?.includes(t)))) throw new Error('Bad toppings');
  if (o.note !== undefined && (typeof o.note !== 'string' || o.note.length > 120)) throw new Error('Bad note');
  const desc = [o.style, o.sauce, o.toppings?.join(', '), o.dip && `with ${o.dip} dip`, o.note && `Note: ${o.note}`].filter(Boolean).join(' · ');
  return { name: it.name, desc, cents: it.cents, qty: l.qty };
};

const api = {
  'GET /api/config': async () => ({ publishableKey: SK && PK ? PK : null }),

  'POST /api/checkout': async (body, req) => {
    if (!SK) throw new Error('Payments are not set up');
    const { items, customer: c } = body;
    if (!Array.isArray(items) || !items.length || items.length > 30) throw new Error('Empty order');
    if (typeof c?.name !== 'string' || !c.name.trim() || c.name.length > 60) throw new Error('Name needed');
    if (typeof c.phone !== 'string' || c.phone.replace(/\D/g, '').length < 10 || c.phone.length > 20) throw new Error('Phone needed');
    if (typeof c.pickup !== 'string' || !/^\d{4}-\d\d-\d\d \d\d:\d\d$/.test(c.pickup)) throw new Error('Pickup time needed');
    const params = { ui_mode: 'embedded', mode: 'payment', redirect_on_completion: 'never',
      'metadata[name]': c.name.trim(), 'metadata[phone]': c.phone, 'metadata[pickup]': c.pickup,
      'payment_intent_data[description]': `Pickup ${c.pickup} for ${c.name.trim()}` };
    items.map(line).forEach((l, i) => {
      params[`line_items[${i}][quantity]`] = l.qty;
      params[`line_items[${i}][price_data][currency]`] = 'usd';
      params[`line_items[${i}][price_data][unit_amount]`] = l.cents;
      params[`line_items[${i}][price_data][product_data][name]`] = l.name;
      if (l.desc) params[`line_items[${i}][price_data][product_data][description]`] = l.desc;
    });
    const s = await stripe('checkout/sessions', params);
    return { id: s.id, clientSecret: s.client_secret };
  },

  'GET /api/order': async (_, req, url) => {
    const id = url.searchParams.get('session') || '';
    if (!/^cs_[A-Za-z0-9_]+$/.test(id)) throw new Error('Bad session');
    const s = await stripe(`checkout/sessions/${id}?expand[]=line_items`, null, 'GET');
    const ref = 'M-' + id.slice(-4).toUpperCase();
    if (s.status === 'complete' && s.payment_status === 'paid' && !recorded.has(id)) {
      recorded.add(id);
      const order = { ref, at: new Date().toISOString(), ...s.metadata, total: s.amount_total,
        items: s.line_items.data.map((x) => ({ qty: x.quantity, name: x.description, amount: x.amount_total })) };
      await appendFile(join(ROOT, 'orders.jsonl'), JSON.stringify(order) + '\n');
      console.log('NEW ORDER', ref, order.pickup, order.name, order.items.map((x) => `${x.qty}× ${x.name}`).join(', '));
    }
    return { ref, status: s.status, paid: s.payment_status === 'paid' };
  },
};

const send = (res, code, type, data) => { res.writeHead(code, { 'Content-Type': type, 'X-Content-Type-Options': 'nosniff' }); res.end(data); };

createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const route = api[`${req.method} ${url.pathname}`];
  if (route) {
    try {
      let raw = '';
      for await (const chunk of req) { raw += chunk; if (raw.length > 20000) throw new Error('Too large'); }
      const out = await route(raw ? JSON.parse(raw) : {}, req, url);
      return send(res, 200, 'application/json', JSON.stringify(out));
    } catch (e) {
      return send(res, 400, 'application/json', JSON.stringify({ error: e.message }));
    }
  }
  if (req.method !== 'GET' && req.method !== 'HEAD') return send(res, 405, 'text/plain', 'Method not allowed');
  // static files: only web types, only inside this folder, never dotfiles
  let path;
  try { path = normalize(join(ROOT, decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname))); } catch { return send(res, 400, 'text/plain', 'Bad path'); }
  const type = TYPES[extname(path).toLowerCase()];
  if (!type || !path.startsWith(ROOT) || path.slice(ROOT.length).split(sep).some((p) => p.startsWith('.'))) return send(res, 404, 'text/plain', 'Not found');
  try { send(res, 200, type, await readFile(path)); } catch { send(res, 404, 'text/plain', 'Not found'); }
}).listen(PORT, () => console.log(`Much Ado on http://localhost:${PORT} · payments ${SK && PK ? 'on (Stripe)' : 'off, demo mode'}`));
