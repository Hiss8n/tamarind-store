import type { FormEvent } from 'react'
import type { Product } from '../data/products'
import { useProductStore } from '../store/productStore'

type CashoutProps = {
	quantities: Record<string, number>
	products: Product[]
	onBackToCart: () => void
}

function Cashout({ quantities, products, onBackToCart }: CashoutProps) {
	const checkout = useProductStore((state) => state.checkout)
	const isCheckingOut = useProductStore((state) => state.isCheckingOut)
	const checkoutComplete = useProductStore((state) => state.checkoutComplete)
	const checkoutResult = useProductStore((state) => state.checkoutResult)
	const items = products.filter((product) => (quantities[product.name] ?? 0) > 0)
	const subtotal = items.reduce((total, product) => total + product.price * quantities[product.name], 0)
	const itemCount = Object.values(quantities).reduce((total, quantity) => total + quantity, 0)

	async function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault()
		const formData = new FormData(event.currentTarget)
		await checkout({
			name: String(formData.get('name') ?? ''),
			phone: `+254${String(formData.get('phone') ?? '')}`,
		})
	}

	return (
		<section className="cashout-page" aria-labelledby="cashout-title">
			<div className="cashout-heading">
				<p className="eyebrow"><span className="eyebrow-line" /> CHECKOUT</p>
				<h1 id="cashout-title">Let’s make it yours.</h1>
				<p className="section-intro">A few details, then your order is ready.</p>
			</div>
			{checkoutComplete && checkoutResult ? (
				<div className="empty-cart cashout-success" role="status">
					<span className="empty-cart-mark" aria-hidden="true">✓</span>
					<h2>Order placed successfully.</h2>
					<p>Thanks, {checkoutResult.payer_name}. Your order has been received.</p>
					<p>Order reference{checkoutResult.order_ids.length === 1 ? '' : 's'}: {checkoutResult.order_ids.join(', ')}</p>
					<p>Total: ${checkoutResult.total_price.toFixed(2)} USD</p>
					<button className="checkout-button" type="button" onClick={onBackToCart}>Return to your bag</button>
				</div>
			) : items.length === 0 ? (
				<div className="empty-cart">
					<span className="empty-cart-mark" aria-hidden="true">＋</span>
					<h2>Your bag is empty.</h2>
					<p>Add something from the menu before checkout.</p>
					<button className="checkout-button" type="button" onClick={onBackToCart}>Return to your bag</button>
				</div>
			) : (
				<div className="cashout-layout">
					<form className="cashout-form" onSubmit={handleSubmit}>
						<div className="cashout-section-title">
							<span className="step-number">01</span>
							<div><h2>Your details</h2><p>We’ll use these for your M-Pesa payment.</p></div>
						</div>

						<label className="form-field">
							<span>Full name</span>
							<input name="name" type="text" placeholder="Name on your order" autoComplete="name" required />
						</label>
						<label className="form-field">
							<span>M-Pesa phone number</span>
							<div className="phone-input-wrap">
								<span className="phone-prefix">+254</span>
								<input name="phone" type="tel" inputMode="tel" placeholder="7XX XXX XXX" autoComplete="tel-national" pattern="[0-9]{9}" aria-describedby="phone-hint" required />
							</div>
							<small id="phone-hint">Enter 9 digits after +254.</small>
						</label>

						<div className="cashout-section-title payment-title">
							<span className="step-number">02</span>
							<div><h2>Payment method</h2><p>Pay directly to the store’s M-Pesa till.</p></div>
						</div>

						<div className="mpesa-option" aria-label="Selected payment method: M-Pesa till">
							<div className="mpesa-option-top">
								<span className="radio-indicator" aria-hidden="true"><span /></span>
								<span className="mpesa-wordmark">M-PESA</span>
								<span className="selected-label">SELECTED</span>
							</div>
							<p>Pay to Till</p>
							<span className="till-pending">Till details will be provided when payment is connected.</span>
						</div>

						<div className="payment-disclaimer">
							<span aria-hidden="true">i</span>
							<p>Submitting sends your order details to the store. It will not charge your phone.</p>
						</div>
						<button className="checkout-button pay-button" type="submit" disabled={isCheckingOut}>
							{isCheckingOut ? 'Submitting…' : 'Continue to M-Pesa'} <span aria-hidden="true">→</span>
						</button>
						<button className="back-to-cart" type="button" onClick={onBackToCart}>← Back to bag</button>
					</form>

					<aside className="cashout-summary" aria-labelledby="cashout-summary-title">
						<div className="cashout-summary-heading">
							<div><p className="summary-kicker">YOUR ORDER</p><h2 id="cashout-summary-title">Order summary</h2></div>
							<span className="summary-item-count">{itemCount} {itemCount === 1 ? 'item' : 'items'}</span>
						</div>
						<div className="cashout-order-items">
							{items.map((product) => (
								<div className="cashout-order-item" key={product.name}>
									<img src={product.image} alt="" />
									<div><h3>{product.name}</h3><p>Qty {quantities[product.name]}</p></div>
									<strong>${(product.price * quantities[product.name]).toFixed(2)}</strong>
								</div>
							))}
						</div>
						<div className="cashout-total-row"><span>Subtotal</span><strong>${subtotal.toFixed(2)} <small>USD</small></strong></div>
						<p className="cashout-currency-note">Final M-Pesa amount and currency conversion will be confirmed when payment processing is connected.</p>
					</aside>
				</div>
			)}
		</section>
	)
}

export default Cashout
