import { useState, useEffect, useCallback } from 'react'

const API = 'http://localhost:8080/api'

// ── Design tokens ──────────────────────────────────────────────────────────────
const C = {
  red:    '#c0392b',
  redL:   '#e74c3c',
  redBg:  '#fdf2f2',
  pink:   '#f8d7da',
  pinkD:  '#c0392b',
  green:  '#27ae60',
  greenL: '#2ecc71',
  gold:   '#f39c12',
  text:   '#2c2c2c',
  muted:  '#666',
  border: '#e8d5d5',
  bg:     '#fffaf9',
  white:  '#ffffff',
  shadow: 'rgba(192,57,43,0.12)',
}

// ── Helpers ────────────────────────────────────────────────────────────────────
const fmt = (n) => Number(n).toLocaleString('vi-VN') + '₫'
const stars = (n) => '★'.repeat(n) + '☆'.repeat(5 - n)

// ── Cart context (simple state) ────────────────────────────────────────────────
function useCart() {
  const [cart, setCart] = useState([])
  const add = (product) => setCart(prev => {
    const ex = prev.find(i => i.id === product.id)
    if (ex) return prev.map(i => i.id === product.id ? {...i, qty: i.qty + 1} : i)
    return [...prev, {...product, qty: 1}]
  })
  const remove = (id) => setCart(prev => prev.filter(i => i.id !== id))
  const update = (id, qty) => {
    if (qty <= 0) { remove(id); return }
    setCart(prev => prev.map(i => i.id === id ? {...i, qty} : i))
  }
  const clear = () => setCart([])
  const total = cart.reduce((s, i) => s + Number(i.price) * i.qty, 0)
  const count = cart.reduce((s, i) => s + i.qty, 0)
  return { cart, add, remove, update, clear, total, count }
}

// ── Styles ─────────────────────────────────────────────────────────────────────
const css = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: ${C.bg}; color: ${C.text}; font-family: 'Segoe UI', system-ui, sans-serif; }
  a { text-decoration: none; color: inherit; }

  /* Nav */
  .nav { background: ${C.red}; color: #fff; padding: 0 32px; display: flex; align-items: center; justify-content: space-between; height: 64px; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 12px rgba(0,0,0,0.15); }
  .nav-logo { font-size: 22px; font-weight: 700; letter-spacing: -0.5px; cursor: pointer; }
  .nav-links { display: flex; gap: 8px; }
  .nav-btn { background: rgba(255,255,255,0.15); border: none; color: #fff; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 14px; transition: background 0.2s; }
  .nav-btn:hover, .nav-btn.active { background: rgba(255,255,255,0.28); }
  .cart-btn { position: relative; }
  .cart-badge { position: absolute; top: -4px; right: -4px; background: ${C.gold}; color: #fff; border-radius: 50%; width: 18px; height: 18px; font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: 700; }

  /* Hero */
  .hero { background: linear-gradient(135deg, ${C.redBg} 0%, #fff5f5 50%, #fff 100%); padding: 80px 32px 60px; text-align: center; border-bottom: 1px solid ${C.border}; }
  .hero-emoji { font-size: 80px; display: block; margin-bottom: 16px; animation: float 3s ease-in-out infinite; }
  @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-12px)} }
  .hero h1 { font-size: 48px; font-weight: 800; color: ${C.red}; line-height: 1.1; margin-bottom: 12px; }
  .hero p { font-size: 18px; color: ${C.muted}; max-width: 520px; margin: 0 auto 28px; line-height: 1.6; }
  .hero-cta { background: ${C.red}; color: #fff; border: none; padding: 14px 36px; border-radius: 30px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 16px ${C.shadow}; }
  .hero-cta:hover { background: ${C.redL}; transform: translateY(-2px); box-shadow: 0 6px 20px ${C.shadow}; }
  .hero-stats { display: flex; gap: 32px; justify-content: center; margin-top: 36px; flex-wrap: wrap; }
  .hero-stat { text-align: center; }
  .hero-stat-num { font-size: 28px; font-weight: 700; color: ${C.red}; }
  .hero-stat-label { font-size: 13px; color: ${C.muted}; margin-top: 2px; }

  /* Section */
  .section { max-width: 1100px; margin: 0 auto; padding: 48px 32px; }
  .section-title { font-size: 28px; font-weight: 700; color: ${C.red}; margin-bottom: 8px; }
  .section-sub { color: ${C.muted}; margin-bottom: 28px; }

  /* Category filter */
  .filters { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px; }
  .filter-btn { padding: 7px 18px; border-radius: 20px; border: 2px solid ${C.border}; background: #fff; color: ${C.muted}; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.15s; }
  .filter-btn:hover, .filter-btn.active { border-color: ${C.red}; background: ${C.red}; color: #fff; }

  /* Product grid */
  .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }
  .product-card { background: #fff; border: 1px solid ${C.border}; border-radius: 16px; overflow: hidden; transition: all 0.2s; cursor: pointer; }
  .product-card:hover { transform: translateY(-4px); box-shadow: 0 8px 28px ${C.shadow}; border-color: ${C.red}; }
  .product-card-img { background: ${C.redBg}; padding: 28px; text-align: center; font-size: 64px; position: relative; }
  .product-badge { position: absolute; top: 12px; right: 12px; background: ${C.gold}; color: #fff; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; }
  .product-card-body { padding: 16px; }
  .product-name { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
  .product-name-vn { font-size: 12px; color: ${C.muted}; margin-bottom: 8px; }
  .product-price { font-size: 20px; font-weight: 700; color: ${C.red}; margin-bottom: 4px; }
  .product-unit { font-size: 12px; color: ${C.muted}; margin-bottom: 12px; }
  .product-stock { font-size: 12px; color: ${C.green}; margin-bottom: 12px; }
  .add-btn { width: 100%; background: ${C.red}; color: #fff; border: none; padding: 10px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
  .add-btn:hover { background: ${C.redL}; }

  /* Product detail modal */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 16px; }
  .modal { background: #fff; border-radius: 20px; max-width: 640px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 32px; position: relative; }
  .modal-close { position: absolute; top: 16px; right: 16px; background: ${C.border}; border: none; width: 32px; height: 32px; border-radius: 50%; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
  .modal-emoji { font-size: 80px; text-align: center; padding: 20px; background: ${C.redBg}; border-radius: 16px; margin-bottom: 20px; }
  .modal-title { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
  .modal-title-vn { font-size: 15px; color: ${C.muted}; margin-bottom: 12px; }
  .modal-price { font-size: 28px; font-weight: 700; color: ${C.red}; margin-bottom: 8px; }
  .modal-desc { color: ${C.muted}; line-height: 1.7; margin-bottom: 20px; }
  .modal-add { background: ${C.red}; color: #fff; border: none; padding: 14px 32px; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; width: 100%; transition: background 0.2s; }
  .modal-add:hover { background: ${C.redL}; }

  /* Reviews */
  .reviews-title { font-size: 18px; font-weight: 600; margin: 24px 0 16px; }
  .review-card { background: ${C.redBg}; border-radius: 12px; padding: 14px 16px; margin-bottom: 10px; }
  .review-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
  .review-author { font-weight: 600; font-size: 14px; }
  .review-stars { color: ${C.gold}; font-size: 14px; }
  .review-comment { font-size: 14px; color: ${C.muted}; }
  .review-form { margin-top: 16px; }
  .review-form input, .review-form textarea, .review-form select { width: 100%; padding: 10px 12px; border: 1px solid ${C.border}; border-radius: 8px; font-size: 14px; margin-bottom: 10px; outline: none; }
  .review-form input:focus, .review-form textarea:focus { border-color: ${C.red}; }
  .review-submit { background: ${C.green}; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }

  /* Cart */
  .cart-sidebar { position: fixed; right: 0; top: 0; bottom: 0; width: 380px; background: #fff; z-index: 300; box-shadow: -4px 0 24px rgba(0,0,0,0.12); display: flex; flex-direction: column; transform: translateX(100%); transition: transform 0.3s; }
  .cart-sidebar.open { transform: translateX(0); }
  .cart-header { padding: 20px 24px; border-bottom: 1px solid ${C.border}; display: flex; justify-content: space-between; align-items: center; }
  .cart-header h2 { font-size: 20px; font-weight: 700; }
  .cart-close { background: none; border: none; font-size: 24px; cursor: pointer; color: ${C.muted}; }
  .cart-body { flex: 1; overflow-y: auto; padding: 16px 24px; }
  .cart-empty { text-align: center; padding: 60px 0; color: ${C.muted}; font-size: 15px; }
  .cart-item { display: flex; gap: 12px; padding: 14px 0; border-bottom: 1px solid ${C.border}; }
  .cart-item-emoji { font-size: 36px; background: ${C.redBg}; width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .cart-item-info { flex: 1; }
  .cart-item-name { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
  .cart-item-price { font-size: 13px; color: ${C.muted}; }
  .qty-ctrl { display: flex; align-items: center; gap: 8px; margin-top: 8px; }
  .qty-btn { width: 26px; height: 26px; border-radius: 6px; border: 1px solid ${C.border}; background: #fff; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; }
  .qty-btn:hover { background: ${C.redBg}; border-color: ${C.red}; }
  .cart-footer { padding: 20px 24px; border-top: 1px solid ${C.border}; }
  .cart-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: 700; margin-bottom: 16px; }
  .checkout-btn { width: 100%; background: ${C.red}; color: #fff; border: none; padding: 14px; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; }
  .checkout-btn:hover { background: ${C.redL}; }

  /* Checkout */
  .checkout-wrap { max-width: 560px; margin: 0 auto; padding: 48px 32px; }
  .checkout-title { font-size: 28px; font-weight: 700; color: ${C.red}; margin-bottom: 28px; }
  .form-group { margin-bottom: 16px; }
  .form-label { font-size: 13px; font-weight: 600; color: ${C.muted}; margin-bottom: 6px; display: block; }
  .form-input { width: 100%; padding: 12px 14px; border: 1.5px solid ${C.border}; border-radius: 10px; font-size: 15px; outline: none; }
  .form-input:focus { border-color: ${C.red}; }
  .order-summary { background: ${C.redBg}; border-radius: 14px; padding: 20px; margin-bottom: 24px; }
  .order-summary-title { font-size: 15px; font-weight: 600; margin-bottom: 12px; }
  .order-line { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 6px; color: ${C.muted}; }
  .order-total-line { display: flex; justify-content: space-between; font-size: 18px; font-weight: 700; color: ${C.red}; margin-top: 10px; padding-top: 10px; border-top: 1px solid ${C.border}; }
  .place-order-btn { width: 100%; background: ${C.red}; color: #fff; border: none; padding: 16px; border-radius: 12px; font-size: 17px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
  .place-order-btn:hover { background: ${C.redL}; transform: translateY(-1px); }

  /* Success */
  .success-wrap { text-align: center; padding: 80px 32px; }
  .success-emoji { font-size: 72px; display: block; margin-bottom: 20px; }
  .success-title { font-size: 32px; font-weight: 700; color: ${C.green}; margin-bottom: 12px; }
  .success-text { font-size: 16px; color: ${C.muted}; margin-bottom: 28px; }
  .back-btn { background: ${C.red}; color: #fff; border: none; padding: 14px 36px; border-radius: 30px; font-size: 16px; font-weight: 600; cursor: pointer; }

  /* About */
  .about-hero { background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%); color: #fff; padding: 80px 32px; text-align: center; }
  .about-hero h1 { font-size: 40px; font-weight: 800; margin-bottom: 16px; }
  .about-hero p { font-size: 18px; opacity: 0.9; max-width: 560px; margin: 0 auto; }
  .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 16px; }
  .feature-card { background: #fff; border: 1px solid ${C.border}; border-radius: 16px; padding: 24px; text-align: center; }
  .feature-icon { font-size: 40px; display: block; margin-bottom: 12px; }
  .feature-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; color: ${C.red}; }
  .feature-desc { font-size: 14px; color: ${C.muted}; line-height: 1.6; }

  /* Toast */
  .toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); background: ${C.text}; color: #fff; padding: 12px 24px; border-radius: 30px; font-size: 14px; font-weight: 500; z-index: 999; animation: slideUp 0.3s ease; pointer-events: none; white-space: nowrap; }
  @keyframes slideUp { from{opacity:0;transform:translate(-50%,20px)} to{opacity:1;transform:translate(-50%,0)} }

  @media (max-width: 600px) {
    .hero h1 { font-size: 32px; }
    .nav { padding: 0 16px; }
    .section { padding: 32px 16px; }
    .cart-sidebar { width: 100%; }
  }
`

// ── Toast ──────────────────────────────────────────────────────────────────────
function Toast({ msg }) {
  return msg ? <div className="toast">{msg}</div> : null
}

// ── Navbar ─────────────────────────────────────────────────────────────────────
function Navbar({ page, setPage, cartCount, toggleCart }) {
  return (
    <nav className="nav">
      <div className="nav-logo" onClick={() => setPage('home')}>🍈 LycheeShop</div>
      <div className="nav-links">
        <button className={`nav-btn ${page === 'home' ? 'active' : ''}`} onClick={() => setPage('home')}>Home</button>
        <button className={`nav-btn ${page === 'shop' ? 'active' : ''}`} onClick={() => setPage('shop')}>Shop</button>
        <button className={`nav-btn ${page === 'about' ? 'active' : ''}`} onClick={() => setPage('about')}>About</button>
        <button className="nav-btn cart-btn" onClick={toggleCart}>
          🛒 Cart {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </button>
      </div>
    </nav>
  )
}

// ── Product Card ───────────────────────────────────────────────────────────────
function ProductCard({ product, onAdd, onClick }) {
  return (
    <div className="product-card" onClick={() => onClick(product)}>
      <div className="product-card-img">
        <span style={{fontSize:64}}>{product.image_emoji}</span>
        {product.featured && <span className="product-badge">⭐ Featured</span>}
      </div>
      <div className="product-card-body">
        <div className="product-name">{product.name}</div>
        <div className="product-name-vn">{product.name_vn}</div>
        <div className="product-price">{fmt(product.price)}</div>
        <div className="product-unit">per {product.unit}</div>
        <div className="product-stock">✅ {product.stock} in stock</div>
        <button className="add-btn" onClick={e => { e.stopPropagation(); onAdd(product) }}>
          + Add to Cart
        </button>
      </div>
    </div>
  )
}

// ── Product Modal ──────────────────────────────────────────────────────────────
function ProductModal({ product, onClose, onAdd }) {
  const [reviews, setReviews] = useState([])
  const [form, setForm] = useState({ author: '', rating: 5, comment: '' })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetch(`${API}/products/${product.id}/reviews`)
      .then(r => r.json()).then(setReviews).catch(() => {})
  }, [product.id])

  const submitReview = async () => {
    if (!form.author) return
    setSubmitting(true)
    try {
      const res = await fetch(`${API}/products/${product.id}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      const r = await res.json()
      setReviews(prev => [r, ...prev])
      setForm({ author: '', rating: 5, comment: '' })
    } catch {}
    setSubmitting(false)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <div className="modal-emoji">{product.image_emoji}</div>
        <div className="modal-title">{product.name}</div>
        <div className="modal-title-vn">{product.name_vn}</div>
        <div className="modal-price">{fmt(product.price)} <span style={{fontSize:14,color:C.muted,fontWeight:400}}>/ {product.unit}</span></div>
        <div className="modal-desc">{product.description}</div>
        <div style={{display:'flex',gap:12,marginBottom:20}}>
          <span style={{background:C.redBg,color:C.red,padding:'4px 12px',borderRadius:20,fontSize:13}}>📦 {product.category}</span>
          <span style={{background:'#e8f5e9',color:C.green,padding:'4px 12px',borderRadius:20,fontSize:13}}>✅ {product.stock} available</span>
        </div>
        <button className="modal-add" onClick={() => { onAdd(product); onClose() }}>
          🛒 Add to Cart — {fmt(product.price)}
        </button>

        <div className="reviews-title">💬 Customer Reviews ({reviews.length})</div>
        {reviews.length === 0 && <p style={{color:C.muted,fontSize:14}}>No reviews yet. Be the first!</p>}
        {reviews.map(r => (
          <div key={r.id} className="review-card">
            <div className="review-header">
              <span className="review-author">{r.author}</span>
              <span className="review-stars">{stars(r.rating)}</span>
            </div>
            <div className="review-comment">{r.comment}</div>
          </div>
        ))}

        <div className="review-form">
          <div style={{fontWeight:600,marginBottom:10,fontSize:14}}>Leave a review:</div>
          <input className="form-input" placeholder="Your name" value={form.author}
            onChange={e => setForm(p => ({...p, author: e.target.value}))} />
          <select style={{width:'100%',padding:'10px 12px',border:`1px solid ${C.border}`,borderRadius:8,fontSize:14,marginBottom:10,outline:'none'}}
            value={form.rating} onChange={e => setForm(p => ({...p, rating: +e.target.value}))}>
            {[5,4,3,2,1].map(n => <option key={n} value={n}>{stars(n)} ({n} stars)</option>)}
          </select>
          <textarea className="form-input" placeholder="Share your experience..." rows={3}
            value={form.comment} onChange={e => setForm(p => ({...p, comment: e.target.value}))} />
          <button className="review-submit" onClick={submitReview} disabled={submitting}>
            {submitting ? 'Submitting...' : '✓ Submit Review'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Cart Sidebar ───────────────────────────────────────────────────────────────
function CartSidebar({ open, onClose, cart, update, remove, total, onCheckout }) {
  return (
    <div className={`cart-sidebar ${open ? 'open' : ''}`}>
      <div className="cart-header">
        <h2>🛒 Your Cart</h2>
        <button className="cart-close" onClick={onClose}>✕</button>
      </div>
      <div className="cart-body">
        {cart.length === 0
          ? <div className="cart-empty"><span style={{fontSize:48}}>🛒</span><br/><br/>Your cart is empty</div>
          : cart.map(item => (
          <div key={item.id} className="cart-item">
            <div className="cart-item-emoji">{item.image_emoji}</div>
            <div className="cart-item-info">
              <div className="cart-item-name">{item.name}</div>
              <div className="cart-item-price">{fmt(item.price)} / {item.unit}</div>
              <div className="qty-ctrl">
                <button className="qty-btn" onClick={() => update(item.id, item.qty - 1)}>−</button>
                <span style={{fontSize:15,fontWeight:600,minWidth:20,textAlign:'center'}}>{item.qty}</span>
                <button className="qty-btn" onClick={() => update(item.id, item.qty + 1)}>+</button>
                <span style={{marginLeft:'auto',fontWeight:600,color:C.red}}>{fmt(item.price * item.qty)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      {cart.length > 0 && (
        <div className="cart-footer">
          <div className="cart-total"><span>Total</span><span style={{color:C.red}}>{fmt(total)}</span></div>
          <button className="checkout-btn" onClick={onCheckout}>Checkout →</button>
        </div>
      )}
    </div>
  )
}

// ── Pages ──────────────────────────────────────────────────────────────────────

function HomePage({ setPage, onAdd, showToast }) {
  const [featured, setFeatured] = useState([])
  const [stats, setStats] = useState(null)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    fetch(`${API}/featured`).then(r => r.json()).then(setFeatured).catch(() => {})
    fetch(`${API}/stats`).then(r => r.json()).then(setStats).catch(() => {})
  }, [])

  const handleAdd = (p) => { onAdd(p); showToast(`🍈 ${p.name} added to cart!`) }

  return (
    <>
      {/* Hero */}
      <div className="hero">
        <span className="hero-emoji">🍈</span>
        <h1>Premium Lychee<br/>Straight from the Farm</h1>
        <p>Fresh vải thiều from Bắc Giang — hand-picked, same-day delivery. Pure sweetness in every bite.</p>
        <button className="hero-cta" onClick={() => setPage('shop')}>Shop Now →</button>
        {stats && (
          <div className="hero-stats">
            <div className="hero-stat"><div className="hero-stat-num">{stats.products}+</div><div className="hero-stat-label">Products</div></div>
            <div className="hero-stat"><div className="hero-stat-num">{stats.orders}+</div><div className="hero-stat-label">Orders</div></div>
            <div className="hero-stat"><div className="hero-stat-num">{stats.reviews}+</div><div className="hero-stat-label">Reviews</div></div>
            <div className="hero-stat"><div className="hero-stat-num">{'★'.repeat(Math.round(stats.avg_rating))}</div><div className="hero-stat-label">Avg Rating</div></div>
          </div>
        )}
      </div>

      {/* Featured */}
      <div className="section">
        <div className="section-title">⭐ Featured Products</div>
        <div className="section-sub">Our best-selling lychee products</div>
        <div className="product-grid">
          {featured.map(p => (
            <ProductCard key={p.id} product={p} onAdd={handleAdd} onClick={setSelected} />
          ))}
        </div>
        <div style={{textAlign:'center',marginTop:28}}>
          <button onClick={() => setPage('shop')} style={{background:'none',border:`2px solid ${C.red}`,color:C.red,padding:'12px 32px',borderRadius:30,fontSize:15,fontWeight:600,cursor:'pointer'}}>
            View All Products →
          </button>
        </div>
      </div>

      {/* Why us */}
      <div style={{background:C.redBg,padding:'48px 32px'}}>
        <div style={{maxWidth:1100,margin:'0 auto'}}>
          <div className="section-title" style={{textAlign:'center',marginBottom:8}}>Why Choose Us?</div>
          <div className="section-sub" style={{textAlign:'center',marginBottom:24}}>Direct from Bắc Giang orchards to your door</div>
          <div className="feature-grid">
            {[
              ['🌿','100% Natural','No preservatives, no chemicals. Pure lychee goodness.'],
              ['🚚','Same-day Delivery','Harvested in the morning, at your door by evening.'],
              ['❄️','Fresh Guaranteed','Packed with ice to maintain freshness during transport.'],
              ['⭐','Premium Quality','Hand-selected Grade-A lychees only. No compromise.'],
            ].map(([icon, title, desc]) => (
              <div key={title} className="feature-card">
                <span className="feature-icon">{icon}</span>
                <div className="feature-title">{title}</div>
                <div className="feature-desc">{desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selected && <ProductModal product={selected} onClose={() => setSelected(null)} onAdd={handleAdd} />}
    </>
  )
}

function ShopPage({ onAdd, showToast }) {
  const [products, setProducts] = useState([])
  const [category, setCategory] = useState('all')
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)

  const cats = [
    {k:'all',label:'🍈 All'},
    {k:'fresh',label:'🌿 Fresh'},
    {k:'gift',label:'🎁 Gift'},
    {k:'dried',label:'🍂 Dried'},
    {k:'processed',label:'🍯 Processed'},
    {k:'beverage',label:'🍷 Beverage'},
    {k:'frozen',label:'❄️ Frozen'},
  ]

  useEffect(() => {
    setLoading(true)
    const url = category === 'all' ? `${API}/products` : `${API}/products?category=${category}`
    fetch(url).then(r => r.json()).then(d => { setProducts(d); setLoading(false) }).catch(() => setLoading(false))
  }, [category])

  const handleAdd = (p) => { onAdd(p); showToast(`🍈 ${p.name} added!`) }

  return (
    <div className="section">
      <div className="section-title">🛍️ All Products</div>
      <div className="section-sub">Fresh lychee products from Bắc Giang</div>
      <div className="filters">
        {cats.map(c => (
          <button key={c.k} className={`filter-btn ${category === c.k ? 'active' : ''}`}
            onClick={() => setCategory(c.k)}>{c.label}</button>
        ))}
      </div>
      {loading
        ? <div style={{textAlign:'center',padding:'60px',fontSize:48}}>🍈</div>
        : <div className="product-grid">
            {products.map(p => <ProductCard key={p.id} product={p} onAdd={handleAdd} onClick={setSelected} />)}
          </div>
      }
      {selected && <ProductModal product={selected} onClose={() => setSelected(null)} onAdd={handleAdd} />}
    </div>
  )
}

function CheckoutPage({ cart, total, clear, setPage, showToast }) {
  const [form, setForm] = useState({ name: '', email: '', phone: '', address: '' })
  const [placing, setPlacing] = useState(false)
  const [done, setDone] = useState(false)

  if (done) return (
    <div className="success-wrap">
      <span className="success-emoji">🎉</span>
      <div className="success-title">Order Placed!</div>
      <div className="success-text">Thank you for your order. We'll contact you shortly to confirm delivery.</div>
      <button className="back-btn" onClick={() => { clear(); setPage('home') }}>Back to Home</button>
    </div>
  )

  const place = async () => {
    if (!form.name || !form.email) { showToast('⚠️ Name and email required'); return }
    setPlacing(true)
    try {
      const res = await fetch(`${API}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          items: cart.map(i => ({ product_id: i.id, name: i.name, quantity: i.qty, price: i.price }))
        })
      })
      if (res.ok) setDone(true)
      else showToast('❌ Order failed. Please try again.')
    } catch { showToast('❌ Network error') }
    setPlacing(false)
  }

  return (
    <div className="checkout-wrap">
      <div className="checkout-title">🛒 Checkout</div>
      <div className="order-summary">
        <div className="order-summary-title">Order Summary</div>
        {cart.map(i => (
          <div key={i.id} className="order-line">
            <span>{i.image_emoji} {i.name} × {i.qty}</span>
            <span>{fmt(i.price * i.qty)}</span>
          </div>
        ))}
        <div className="order-total-line"><span>Total</span><span>{fmt(total)}</span></div>
      </div>
      {['name','email','phone','address'].map(f => (
        <div key={f} className="form-group">
          <label className="form-label">{f.charAt(0).toUpperCase() + f.slice(1)} {f === 'address' ? '' : f === 'phone' ? '' : '*'}</label>
          <input className="form-input" placeholder={
            f === 'name' ? 'Full name' : f === 'email' ? 'your@email.com' :
            f === 'phone' ? '0909 000 000' : 'Delivery address'
          } value={form[f]} onChange={e => setForm(p => ({...p, [f]: e.target.value}))} />
        </div>
      ))}
      <button className="place-order-btn" onClick={place} disabled={placing}>
        {placing ? 'Placing order...' : `Place Order — ${fmt(total)}`}
      </button>
    </div>
  )
}

function AboutPage() {
  return (
    <>
      <div className="about-hero">
        <h1>🍈 About LycheeShop</h1>
        <p>We bring the finest lychees from the orchards of Bắc Giang directly to your table — fresh, fast, and full of flavour.</p>
      </div>
      <div className="section">
        <div className="section-title">Our Story</div>
        <p style={{color:C.muted,lineHeight:1.8,maxWidth:680,marginBottom:32}}>
          LycheeShop was founded in 2019 by a family from Lục Ngạn, Bắc Giang — home to Vietnam's most prized lychee orchards.
          We saw that the best lychees rarely made it out of the province fresh, so we built a direct supply chain
          that goes from tree to customer in under 24 hours. No middlemen. No chemicals. Just the sweetest lychees you've ever tasted.
        </p>
        <div className="feature-grid">
          {[
            ['🌳','Our Orchard','30 hectares of lychee orchards in Lục Ngạn, Bắc Giang. Organically managed for over 20 years.'],
            ['📦','Packaging','Eco-friendly packaging with food-safe ice packs to maintain freshness during delivery.'],
            ['🚀','Delivery','Same-day delivery to HCM City, Hà Nội, and major cities. Next-day for other provinces.'],
            ['💚','Sustainability','We plant 3 new trees for every 100kg sold. Committed to protecting the lychee heritage.'],
          ].map(([icon, title, desc]) => (
            <div key={title} className="feature-card">
              <span className="feature-icon">{icon}</span>
              <div className="feature-title">{title}</div>
              <div className="feature-desc">{desc}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

// ── App Root ───────────────────────────────────────────────────────────────────
export default function App() {
  const [page, setPage] = useState('home')
  const [cartOpen, setCartOpen] = useState(false)
  const [toast, setToast] = useState('')
  const { cart, add, remove, update, clear, total, count } = useCart()

  const showToast = useCallback((msg) => {
    setToast(msg)
    setTimeout(() => setToast(''), 2500)
  }, [])

  const handleCheckout = () => { setCartOpen(false); setPage('checkout') }

  return (
    <>
      <style>{css}</style>
      <Navbar page={page} setPage={setPage} cartCount={count} toggleCart={() => setCartOpen(o => !o)} />

      {page === 'home'     && <HomePage setPage={setPage} onAdd={add} showToast={showToast} />}
      {page === 'shop'     && <ShopPage onAdd={add} showToast={showToast} />}
      {page === 'about'    && <AboutPage />}
      {page === 'checkout' && <CheckoutPage cart={cart} total={total} clear={clear} setPage={setPage} showToast={showToast} />}

      <CartSidebar open={cartOpen} onClose={() => setCartOpen(false)}
        cart={cart} update={update} remove={remove} total={total} onCheckout={handleCheckout} />

      {cartOpen && <div style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.3)',zIndex:299}} onClick={() => setCartOpen(false)} />}

      <Toast msg={toast} />

      {/* Footer */}
      <footer style={{background:C.red,color:'#fff',padding:'32px',textAlign:'center',marginTop:40}}>
        <div style={{fontSize:32,marginBottom:8}}>🍈</div>
        <div style={{fontWeight:700,fontSize:18,marginBottom:6}}>LycheeShop</div>
        <div style={{opacity:0.8,fontSize:14}}>Fresh vải thiều Bắc Giang · React + Python + PostgreSQL + Docker 🐳</div>
      </footer>
    </>
  )
}
