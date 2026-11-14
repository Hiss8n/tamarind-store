import type { Product } from '../data/products'

type CartProps = {
	quantities: Record<string, number>
	products: Product[]
	onQuantityChange: (name: string, change: number) => void
	onContinueShopping: () => void
	onCheckout: () => void
}

function Cart({ quantities, products, onQuantityChange, onContinueShopping, onCheckout }: CartProps) {
	const cartItems = products.filter((product) => (quantities[product.name] ?? 0) > 0)
	const subtotal = cartItems.reduce((total, product) => total + product.price * quantities[product.name], 0)

	return (
		<section className="cart-page" aria-labelledby="cart-title">
			<div className="cart-heading">
				<p className="eyebrow"><span className="eyebrow-line" /> YOUR MARKET BAG</p>
				<h1 id="cart-title">A good choice.</h1>
				<p className="section-intro">Everything for your table, all in one place.</p>
			</div>

			{cartItems.length === 0 ? (
				<div className="empty-cart">
					<span className="empty-cart-mark" aria-hidden="true">＋</span>
					<h2>Your bag is taking a breather.</h2>
					<p>Find something fresh for the table.</p>
					<button className="checkout-button" type="button" onClick={onContinueShopping}>Browse the menu</button>
				</div>
			) : (
				<div className="cart-layout">
					<div className="cart-items">
						<div className="cart-list-heading">
							<h2>Your items <span>({cartItems.length})</span></h2>
							<button className="text-button" type="button" onClick={onContinueShopping}>Continue shopping <span aria-hidden="true">→</span></button>
						</div>
						{cartItems.map((product) => {
							const quantity = quantities[product.name]
							return (
								<article className="cart-item" key={product.name}>
									<img src={product.image} alt={product.imageAlt} />
									<div className="cart-item-copy">
										<p className="cart-item-tag">{product.tag}</p>
										<h3>{product.name}</h3>
										<p>{product.description}</p>
									</div>
									<div className="cart-item-controls">
										<span className="cart-item-price">${product.price.toFixed(2)}</span>
										<div className="quantity-control" aria-label={`${product.name} quantity`}>
											<button type="button" aria-label={`Remove one ${product.name}`} onClick={() => onQuantityChange(product.name, -1)}>−</button>
											<span aria-live="polite">{quantity}</span>
											<button type="button" aria-label={`Add one ${product.name}`} onClick={() => onQuantityChange(product.name, 1)}>+</button>
										</div>
									</div>
								</article>
							)
						})}
					</div>

					<aside className="order-summary" aria-labelledby="summary-title">
						<p className="summary-kicker">THE TOTAL</p>
						<h2 id="summary-title">Order summary</h2>
						<div className="summary-row"><span>Items ({Object.values(quantities).reduce((total, quantity) => total + quantity, 0)})</span><span>${subtotal.toFixed(2)}</span></div>
						<div className="summary-row"><span>Delivery</span><span className="delivery-note">At checkout</span></div>
						<div className="summary-total"><span>Subtotal</span><strong>${subtotal.toFixed(2)} <small>USD</small></strong></div>
						<button className="checkout-button" type="button" onClick={onCheckout}>Continue to checkout <span aria-hidden="true">→</span></button>
						<p className="summary-footnote">Taxes and delivery are calculated at checkout.</p>
					</aside>
				</div>
			)}
		</section>
	)
}

export default Cart
