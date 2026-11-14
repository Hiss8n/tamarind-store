# Tamarind Market Frontend

## Store Overview

Tamarind Market is a small online food store. The frontend lets a customer browse a product catalog, add products to a shopping cart, change item quantities, review an order, and enter customer details on a checkout page. The current interface is a React application with three client-side views: Shop, Cart, and Cashout.

This document describes behavior visible in the code under `frontend/` and outlines backend responsibilities needed to support that behavior. It does not describe the separate backend implementation.

## Customer Flow

1. **Browse products.** The Shop view displays each product's name, description, price in USD, image, image alternative text, and merchandising tag. The current catalog contains Kisra, Soda, Anjera, Chapati, Salad, and Spaghetti.
2. **Add products.** An item initially has an Add button. Selecting it adds one unit and changes the control to decrement, quantity, and increment buttons. These controls are also available on cart items.
3. **Review the cart.** The navigation bar displays the total number of units. The Cart view lists only products with a positive quantity, shows unit prices and a subtotal, and offers continue-shopping and checkout actions. Decreasing a quantity to zero removes that item. An empty cart has a prompt to return to the menu.
4. **Checkout.** The Cashout view summarizes the selected items, quantities, and subtotal. If the cart is empty, it offers a return-to-cart action. Otherwise, the customer enters a required full name and a required nine-digit phone number; the interface displays the country prefix `+254` and describes the number as an M-Pesa phone number. M-Pesa till is the displayed payment method. A back action returns to the cart.
5. **Payment status.** The current checkout submission only displays a notice that payment requests are not connected. It does not create an order, send an M-Pesa request, or charge the customer.

## Current Frontend Behavior

- The catalog is a hard-coded array in `src/data/products.ts`; it is not loaded from a server.
- Cart quantities are held in React state in `src/App.tsx`, keyed by product name. They are shared between the Shop, Cart, and Cashout views while the app remains open, but are not persisted across reloads or devices.
- The cart count is the sum of quantities. The cart's displayed item count in its heading is the number of distinct products, while the order summary and checkout summary show total units.
- The cart and checkout subtotals are calculated in the browser as the sum of unit price multiplied by quantity. Delivery is described as determined at checkout, but no delivery fee, tax, or final total is currently calculated.
- Navigation switches views in the client; it does not change the browser route.
- Prices are formatted with a `$` sign and labeled USD in the catalog and checkout. The checkout notes that final M-Pesa amount and currency conversion are not yet connected.
- The customer form requires a name and a phone number matching nine digits after the displayed `+254` prefix. Browser form validation runs before its current preview submission handler.

## Catalog Data

Each product currently has these frontend fields:

| Field | Purpose |
| --- | --- |
| `name` | Display name and current cart key |
| `description` | Short product description |
| `price` | Unit price, currently represented as a number |
| `image` | Product image URL |
| `imageAlt` | Accessible description of the image on the Shop and Cart views |
| `tag` | Short merchandising label |

For a backend-backed catalog, use a stable product ID rather than the product name as the cart key. The server should own the authoritative product price and availability; a submitted order must not trust prices sent by the browser.

## Backend Capabilities Needed

The frontend behavior implies the following backend capabilities. These are implementation requirements to build toward, not features currently connected to this UI.

- **Product catalog:** return active products with a stable ID, display name, description, unit price, currency, image URL, image alt text, tag, and availability. The Shop view needs enough information to render the existing product listing.
- **Cart:** create or retrieve a cart, add a product, update its quantity, and remove it when quantity reaches zero. Validate that quantities are positive integers for stored lines, and reject unavailable or unknown products. Persist the cart if it should survive a reload or be shared across sessions.
- **Cart summary:** return line items with current product details, quantities, line totals, and a server-calculated subtotal. The frontend currently has no delivery or tax rules; return those separately if they are introduced, and define when they are calculated.
- **Checkout/order creation:** accept customer name, phone number, and the cart reference or selected product IDs and quantities. Revalidate product availability and calculate all prices and totals on the server. Create an order snapshot so later catalog price changes do not rewrite an existing order.
- **Payment integration:** initiate M-Pesa payment only after an order is successfully created, using server-side credentials and the verified order amount. Track pending, successful, failed, and cancelled payment states, and use the payment provider's callback/status mechanism to confirm payment. Never report payment success merely because the customer submitted the form.
- **Checkout response:** return an order reference and a clear payment/order status for the UI to show. The current form has no success, failure, or pending state beyond its preview notice, so those states will need to be added when payment is connected.

## Suggested API Shape

The exact routes are a backend design choice. A resource-oriented API could provide:

| Method and path | Purpose |
| --- | --- |
| `GET /api/products` | List active products for the Shop view |
| `GET /api/cart` | Retrieve the current customer's cart and calculated summary |
| `POST /api/cart/items` | Add a product or quantity to the cart |
| `PATCH /api/cart/items/{productId}` | Set a cart line's quantity; remove the line at zero if that is the chosen contract |
| `DELETE /api/cart/items/{productId}` | Remove a cart line explicitly |
| `POST /api/orders` | Validate customer/cart data and create an order |
| `POST /api/orders/{orderId}/payments` | Start the M-Pesa payment process for an order |
| `GET /api/orders/{orderId}` | Retrieve order and payment status for the customer-facing result view |

For each mutation, return the updated cart or order summary so the UI can stay synchronized with server-calculated values. Protect customer and payment endpoints appropriately, validate all inputs on the server, and avoid returning secrets or sensitive provider data to the browser.

## Frontend Integration Notes

When connecting the API, replace the hard-coded product source with catalog data from the backend and replace local-only quantity updates with cart requests. Keep the UI responsive while requests are pending, show useful validation and network errors, and prevent duplicate checkout submissions. If anonymous shopping is supported, decide how the frontend identifies and retains the customer's cart; if accounts are added, associate carts and orders with the authenticated customer.

The current checkout copy says the M-Pesa till details will be provided when payment is connected. Update that content to match the actual payment flow once the till or provider integration is configured. Do not collect or store a payment PIN in this application.
