import { create } from 'zustand'
import { products } from '../data/products'

type CheckoutDetails = {
	name: string
	phone: string
}

type ProductStore = {
	quantities: Record<string, number>
	error: string | null
	isCheckingOut: boolean
	checkoutComplete: boolean
	addToCart: (name: string) => void
	removeFromCart: (name: string) => void
	decreaseCartQuantity: (name: string) => void
	updateCartQuantity: (name: string, quantity: number) => void
	clearCart: () => void
	checkout: (details: CheckoutDetails) => Promise<void>
	clearError: () => void
}

function logDocument(action: string, document: unknown) {
	console.log(`[productStore] ${action}`, document)
}

export const useProductStore = create<ProductStore>((set, get) => ({
	quantities: {},
	error: null,
	isCheckingOut: false,
	checkoutComplete: false,
	addToCart: (name) => {
		const quantity = (get().quantities[name] ?? 0) + 1
		const product = products.find((item) => item.name === name)
		set((state) => ({
			quantities: { ...state.quantities, [name]: quantity },
			error: null,
			checkoutComplete: false,
		}))
		logDocument('cart item added', { name, quantity, price: product?.price })
	},
	removeFromCart: (name) => {
		set((state) => {
			const quantities = { ...state.quantities }
			delete quantities[name]
			return { quantities, error: null, checkoutComplete: false }
		})
		logDocument('cart item removed', { name })
	},
	decreaseCartQuantity: (name) => {
		const quantity = Math.max(0, (get().quantities[name] ?? 0) - 1)
		if (quantity === 0) {
			get().removeFromCart(name)
			return
		}
		get().updateCartQuantity(name, quantity)
	},
	updateCartQuantity: (name, quantity) => {
		const nextQuantity = Math.max(0, Math.floor(quantity))
		if (nextQuantity === 0) {
			get().removeFromCart(name)
			return
		}
		const product = products.find((item) => item.name === name)
		set((state) => ({
			quantities: { ...state.quantities, [name]: nextQuantity },
			error: null,
			checkoutComplete: false,
		}))
		logDocument('cart item updated', {
			name,
			quantity: nextQuantity,
			price: product?.price,
		})
	},
	clearCart: () => {
		const documents = Object.entries(get().quantities).map(([name, quantity]) => ({
			name,
			quantity,
			price: products.find((product) => product.name === name)?.price,
		}))
		logDocument('cart cleared', documents)
		set({ quantities: {}, error: null, checkoutComplete: false })
	},
	checkout: async (details) => {
		const quantities = get().quantities
		const items = products
			.filter((product) => (quantities[product.name] ?? 0) > 0)
			.map((product) => ({
				name: product.name,
				quantity: quantities[product.name],
				price: product.price,
			}))
		const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0)

		if (items.length === 0) {
			set({ error: 'Your cart is empty.' })
			return
		}

		set({ isCheckingOut: true, error: null, checkoutComplete: false })
		logDocument('order submitted', { ...details, items, total })
		set({ quantities: {}, checkoutComplete: true, isCheckingOut: false })
	},
	clearError: () => set({ error: null }),
}))