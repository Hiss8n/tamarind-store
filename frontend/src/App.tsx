
import { useState } from 'react'
import Cart from './components/cat'
import Navbar, { type Page } from './components/navbar'
import TamarinChat from './components/tamarinChat'
import { products } from './data/products'
import Cashout from './pages/cashout'
import Shop from './pages/shop'
import { useProductStore } from './store/productStore'
import './App.css'

function App() {
  const [activePage, setActivePage] = useState<Page>('shop')
  const quantities = useProductStore((state) => state.quantities)
  const addToCart = useProductStore((state) => state.addToCart)
  const decreaseCartQuantity = useProductStore((state) => state.decreaseCartQuantity)
  const error = useProductStore((state) => state.error)
  const cartCount = Object.values(quantities).reduce((total, quantity) => total + quantity, 0)

  function changeQuantity(name: string, change: number) {
    if (change > 0) addToCart(name)
    else decreaseCartQuantity(name)
  }

  return (
    <div className="store-page" id="top">
      <Navbar cartCount={cartCount} activePage={activePage} onNavigate={setActivePage} />
      <main>
        {error && <p className="cashout-notice" role="alert">{error}</p>}
        {activePage === 'shop' ? (
          <Shop quantities={quantities} />
        ) : activePage === 'cart' ? (
          <Cart
            quantities={quantities}
            products={products}
            onQuantityChange={changeQuantity}
            onContinueShopping={() => setActivePage('shop')}
            onCheckout={() => setActivePage('cashout')}
          />
        ) : (
          <Cashout
            quantities={quantities}
            products={products}
            onBackToCart={() => setActivePage('cart')}
          />
        )}
      </main>
      <TamarinChat />
    </div>
  )
}

export default App
