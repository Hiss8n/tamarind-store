import { create } from 'zustand'
import { products } from '../data/products'


type CheckoutDetails = {
	name: string
	phone: string
}

type CheckoutResult = {
	order_ids: number[]
	total_price: number
	status: string
	payer_name: string
	payer_phone: string
}

type StkPushResult = {
	MerchantRequestID?: string
	CheckoutRequestID?: string
	ResponseCode?: string
	ResponseDescription?: string
	CustomerMessage?: string
}

type ProductStore = {
	quantities: Record<string, number>
	error: string | null
	isCheckingOut: boolean
	checkoutComplete: boolean
	checkoutResult: CheckoutResult | null
	stkPushResult: StkPushResult | null
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
	checkoutResult: null,
	stkPushResult: null,
	addToCart: (name) => {
		const quantity = (get().quantities[name] ?? 0) + 1
		const product = products.find((item) => item.name === name)
		set((state) => ({
			quantities: { ...state.quantities, [name]: quantity },
			error: null,
			checkoutComplete: false,
			checkoutResult: null,
			stkPushResult: null,
		}))
		logDocument('cart item added', { name, quantity, price: product?.price })
	},
	removeFromCart: (name) => {
		set((state) => {
			const quantities = { ...state.quantities }
			delete quantities[name]
			return { quantities, error: null, checkoutComplete: false, checkoutResult: null }
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
			checkoutResult: null,
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
		set({ quantities: {}, error: null, checkoutComplete: false, checkoutResult: null })
	},
	checkout: async (details) => {
		const quantities = get().quantities
		const items = products
			.filter((product) => (quantities[product.name] ?? 0) > 0)
			.map((product) => ({
				product_id: product.product_id,
				name: product.name,
				quantity: quantities[product.name],
				price: product.price,
			}))
		const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0)

		if (items.length === 0) {
			set({ error: 'Your cart is empty.' })
			return
		}

		set({ isCheckingOut: true, error: null, checkoutComplete: false, checkoutResult: null })
		logDocument('order submitted order sent to backend', { ...details, items, total })

		try {
			const apiUrl = import.meta.env.VITE_PUBLIC_URL.replace(/\/+$/, '')
			const response = await fetch(`${apiUrl}/orders/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					...details,
					items,
					total_price: total,
					status: 'pending',
				}),
			})

			if (!response.ok) {
				const errorBody = await response.json().catch(() => null) as { detail?: string | { msg?: string }[] } | null
				const detail = errorBody?.detail
				const message = Array.isArray(detail)
					? detail.map((issue) => issue.msg).filter(Boolean).join(' ')
					: detail
				throw new Error(message || 'Checkout could not be submitted. Please try again.')
			}

			const result = await response.json() as CheckoutResult

			const stkResponse = await fetch(`${apiUrl}/stkpush`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					phone: details.phone,
					amount: Math.max(1, Math.ceil(result.total_price)),
					account_reference: `ORDER-${result.order_ids[0]}`.slice(0, 12),
					description: 'Tamarind',
					order_ids: result.order_ids,
				}),
			})

			if (!stkResponse.ok) {
				const errorBody = await stkResponse.json().catch(() => null) as { detail?: string | { msg?: string }[] } | null
				const detail = errorBody?.detail
				const message = Array.isArray(detail)
					? detail.map((issue) => issue.msg).filter(Boolean).join(' ')
					: detail
				throw new Error(message || 'M-Pesa payment could not be started.')
			}

			const stkResult = await stkResponse.json() as StkPushResult
			set({
				quantities: {},
				checkoutComplete: true,
				checkoutResult: result,
				stkPushResult: stkResult,
			})
		} catch (error) {
			set({ error: error instanceof Error ? error.message : 'Checkout could not be submitted.' })
		} finally {
			set({ isCheckingOut: false })
		}
	},
	clearError: () => set({ error: null }),
}))