export type Product = {
	product_id: number
	name: string
	description: string
	price: number
	image: string
	imageAlt: string
	tag: string
}

export const products: Product[] = [
	{
		product_id: 1,
		name: 'Cookies',
		description: 'Soft, fermented sorghum flatbread',
		price: 20,
		image: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=720&q=85',
		imageAlt: 'Freshly baked flatbread',
		tag: 'House favorite',
	},
	{
		product_id: 2,
		name: 'Cold Drinks',
		description: 'A chilled, sparkling refreshment',
		price: 12,
		image: 'https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=720&q=85',
		imageAlt: 'Cold citrus drink with fresh fruit',
		tag: 'Cold drinks',
	},
	{
		product_id: 3,
		name: 'Anjera',
		description: 'Tender, tangy Ethiopian-style injera',
		price: 15,
		image: 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=720&q=85',
		imageAlt: 'A freshly prepared traditional meal',
		tag: 'Made fresh',
	},
	{
		product_id: 4,
		name: 'Samosa',
		description: 'Golden layered flatbread, made by hand',
		price: 10,
		image: 'https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=720&q=85',
		imageAlt: 'Golden handmade bread served warm',
		tag: 'Made fresh',
	},
	{
		product_id: 5,
		name: 'Salad',
		description: 'Crisp greens, seasonal vegetables',
		price: 16,
		image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=720&q=85',
		imageAlt: 'Fresh green salad with seasonal vegetables',
		tag: 'Plant-forward',
	},
	{
		product_id: 6,
		name: 'Spaghetti',
		description: 'Slow-simmered tomato sauce, fresh herbs',
		price: 17,
		image: 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=720&q=85',
		imageAlt: 'A bowl of spaghetti with tomato sauce',
		tag: 'Comfort food',
	},
]