import { products } from '../data/products'
import { useProductStore } from '../store/productStore'

type ShopProps = {
	quantities: Record<string, number>
}

function Shop({ quantities }: ShopProps) {
	const addToCart = useProductStore((state) => state.addToCart)
	const decreaseCartQuantity = useProductStore((state) => state.decreaseCartQuantity)

	function changeQuantity(name: string, change: number) {
		if (change > 0) addToCart(name)
		else decreaseCartQuantity(name)
	}

	return (
		<>
			<section className="menu-section" id="menu" aria-labelledby="menu-title">
					<div className="section-heading">
						<p className="eyebrow"><span className="eyebrow-line" /> GOOD FOOD, GATHERED</p>
						<h1 id="menu-title">A little taste<br /><em>of home.</em></h1>
						<p className="section-intro">Fresh favorites for your table. Pick something lovely.</p>
					</div>

					<div className="product-grid">
						{products.map((product) => {
							const quantity = quantities[product.name] ?? 0
							return (
								<article className="product" key={product.name}>
									<div className="product-image-wrap">
										<img className="product-image" src={product.image} alt={product.imageAlt} />
										<span className="product-tag">{product.tag}</span>
									</div>
									<div className="product-details">
										<div className="product-copy">
											<h2>{product.name}</h2>
											<p>{product.description}</p>
										</div>
										<div className="product-buy-row">
											<span className="product-price">${product.price.toFixed(2)} <small>USD</small></span>
											{quantity === 0 ? (
											<button className="add-button" type="button" onClick={() => changeQuantity(product.name, 1)}>
													<span aria-hidden="true">+</span> Add
												</button>
											) : (
												<div className="quantity-control" aria-label={`${product.name} quantity`}>
													<button type="button" aria-label={`Remove one ${product.name}`} onClick={() => changeQuantity(product.name, -1)}>−</button>
													<span aria-live="polite">{quantity}</span>
													<button type="button" aria-label={`Add one ${product.name}`} onClick={() => changeQuantity(product.name, 1)}>+</button>
												</div>
											)}
										</div>
									</div>
								</article>
							)
						})}
					</div>
			</section>

				<section className="story-strip" id="story">
					<span className="story-star" aria-hidden="true">✳</span>
					<p>Made with care. Best shared around the table.</p>
					<span className="story-note">TAMARIND MARKET · GOOD THINGS, DAILY</span>
				</section>
		</>
	)
}

export default Shop
