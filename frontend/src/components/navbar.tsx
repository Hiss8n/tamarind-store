export type Page = 'shop' | 'cart' | 'cashout'

type NavbarProps = {
	cartCount: number
	activePage: Page
	onNavigate: (page: Page) => void
}

function Navbar({ cartCount, activePage, onNavigate }: NavbarProps) {
	return (
		<header className="site-header">
			<button className="brand brand-button" type="button" onClick={() => onNavigate('shop')} aria-label="Tamarind Market home">
				<span className="brand-mark" aria-hidden="true">
					T</span>
				<span>Tamarind <span className="brand-light">Market</span></span>
			</button>

			<nav className="main-nav" aria-label="Main navigation">
				<button className={`nav-link ${activePage === 'shop' ? 'nav-link-active' : ''}`} type="button" onClick={() => onNavigate('shop')}>Shop</button>
				<button className="nav-link" type="button" onClick={() => onNavigate('shop')}>Our table</button>
			</nav>

			<button className={`bag-link ${activePage !== 'shop' ? 'bag-link-active' : ''}`} type="button" onClick={() => onNavigate('cart')} aria-label={`Shopping bag, ${cartCount} items`}>
				<span>Cart</span>
				<span className="bag-count" aria-live="polite">{cartCount}</span>
			</button>
		</header>
	)
}

export default Navbar
