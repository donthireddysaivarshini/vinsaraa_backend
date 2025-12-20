# Admin Panel Quick Reference

## Admin Dashboard Structure

```
Django Administration
│
├── STORE
│   ├── Categories
│   │   └── [Manage product categories]
│   ├── Products
│   │   └── [Includes inline editing for Variants & Images]
│   ├── Coupons
│   │   └── [Manage discount codes]
│   └── Miscellaneous Charges
│       └── [Shipping rates, taxes - SiteConfig model]
│
├── ORDERS
│   ├── Orders ⭐ NEW: Address column!
│   │   Columns: ID | User | Total Amount | Address | Payment Status | Order Status
│   │   └── [Click dropdown to change status: Processing→Shipped→Delivered]
│   └── Order Items
│       └── [View items in each order]
│
└── ACCOUNTS
    └── Users
        └── [Manage customer accounts]

HIDDEN FROM ADMIN (API managed):
├── Cart (auto-hidden)
├── CartItem (auto-hidden)
├── SavedAddress (auto-hidden)
├── ProductImage (managed via Product)
└── ProductVariant (managed via Product)
```

---

## Orders Admin - Column Layout

### Before (Old)
```
ID | User | Total Amount | Payment Status | Order Status
```

### After (New) ✨
```
ID | User | Total Amount | Address | Payment Status | Order Status
                                    ↑
                              NEW COLUMN!
```

---

## How to Use

### Change Order Status
1. Go to `/admin/orders/order/`
2. Find the order
3. Click the **Status** dropdown (Processing/Shipped/Delivered)
4. Click **SAVE** at the bottom
5. ✅ Status updated (customer sees it in 30s auto-refresh)

### View Order Address
1. In orders list, see address preview in the "Address" column
2. Click order ID to view full address in detail page
3. Address shown in "Address & Contact" section

### Manage Coupons
1. Go to `/admin/store/coupon/`
2. Add/edit discount codes
3. Set discount type: percentage or fixed amount
4. Mark active/inactive

### Configure Shipping & Taxes
1. Go to `/admin/store/miscellaneous-charges/` (or Site Config)
2. Edit:
   - Shipping flat rate
   - Free shipping above amount
   - Tax percentage

---

## Cart Issue Solution

**Problem:** Items still in cart after checkout

**Backend:** Already clears cart ✅
```python
# orders/views.py - CheckoutView
user_cart = Cart.objects.get(user=request.user)
user_cart.items.all().delete()  # ← Clears after order created
```

**Frontend:** Add this to your checkout success handler
```javascript
// After Razorpay payment success
const handlePaymentSuccess = async (paymentData) => {
  // Verify payment with backend
  await verifyPayment(paymentData);
  
  // Clear cart state
  setCart([]); // Clear cart items
  setCartCount(0); // Reset count
  localStorage.removeItem('cart'); // Clear storage
  
  // Show success & redirect
  toast.success("Order placed successfully!");
  navigate('/order-history');
};
```

---

## Admin URLs

| Page | URL | What's There |
|------|-----|-------------|
| Admin Home | `/admin/` | Dashboard |
| Orders | `/admin/orders/order/` | All orders with ADDRESS column |
| Products | `/admin/store/product/` | Products (manage variants inline) |
| Categories | `/admin/store/category/` | Categories |
| Coupons | `/admin/store/coupon/` | Discount codes |
| Charges | `/admin/store/siteconfig/` | Shipping & tax config |
| Users | `/admin/accounts/customuser/` | Customer accounts |

---

## Features Checklist

- ✅ Address column visible in orders list
- ✅ Address preview (first line, 50 chars)
- ✅ Full address in order details
- ✅ Status dropdown (Processing/Shipped/Delivered)
- ✅ Cart/CartItem hidden from admin
- ✅ SavedAddress hidden from admin
- ✅ ProductImage/Variant managed inline
- ✅ SiteConfig as "Miscellaneous Charges"
- ✅ Cart clears on checkout (backend)
- ⏳ Cart clears on checkout (frontend - update needed)

---

## Keyboard Shortcuts

- `/admin/` - Go to admin home
- Tab through form fields
- Ctrl+S or Cmd+S - Save changes (works in some browsers)
- Escape - Cancel/close

---

Made with ❤️ for easier admin management!
