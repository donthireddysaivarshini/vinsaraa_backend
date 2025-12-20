# Implementation Guide: Selective Cart Removal

## Quick Summary

**Instead of** `localStorage.removeItem('cart')` (clears everything)
**Use** selective removal by SKU + Size (removes only purchased items)

---

## 3 Steps to Implement

### Step 1: Update Checkout.tsx
Replace lines 264-275 with the new removal logic

**Find this:**
```javascript
// C. Clear Cart & Redirect
localStorage.removeItem('cart');
toast.success("Payment successful! Redirecting to orders...");
```

**Replace with:**
```javascript
// C. Remove Only Purchased Items from Cart
const purchasedItemKeys = payload.items.map(item => `${item.sku}-${item.size}`);

const currentCart = JSON.parse(localStorage.getItem('cart') || '[]');

const updatedCart = currentCart.filter((item: any) => {
  const itemKey = `${item.sku}-${item.size}`;
  return !purchasedItemKeys.includes(itemKey);
});

if (updatedCart.length > 0) {
  localStorage.setItem('cart', JSON.stringify(updatedCart));
} else {
  localStorage.removeItem('cart');
}

toast.success("Payment successful! Redirecting to orders...");
```

---

### Step 2 (Optional): Update CartContext

If you want React state to sync with localStorage:

**Add this method to CartContext:**
```typescript
const removeMultipleItems = (items: Array<{sku: string, size: string}>) => {
  const updatedItems = cartItems.filter(item => {
    return !items.some(i => i.sku === item.sku && i.size === item.size);
  });
  
  setCartItems(updatedItems);
  localStorage.setItem('cart', JSON.stringify(updatedItems));
};
```

**Export it:**
```typescript
export const CartContext = createContext<CartContextType>({
  // ... other methods
  removeMultipleItems,
});
```

---

### Step 3 (Optional): Use in Checkout

If you implemented Step 2, call it after payment success:

```javascript
import { useCart } from "@/pages/CartContext";

const { removeMultipleItems } = useCart();

// In payment handler, after saving address:
removeMultipleItems(
  payload.items.map(item => ({
    sku: item.sku,
    size: item.size
  }))
);
```

---

## File Provided

**CHECKOUT_UPDATED.tsx** - Complete updated checkout with selective removal built-in

Just copy this file to `src/pages/Checkout.tsx`

---

## Example Scenarios

### Scenario 1: Buy 1 Item
```
Before: [Shirt-M, Pants-L]
Buying: [Shirt-M]
After:  [Pants-L]  ✅
```

### Scenario 2: Buy All Items
```
Before: [Shirt-M, Pants-L]
Buying: [Shirt-M, Pants-L]
After:  []  ✅
```

### Scenario 3: Partial Purchase
```
Before: [Shirt-M, Pants-L, Hat-One]
Buying: [Shirt-M, Hat-One]
After:  [Pants-L]  ✅
```

---

## How Items are Matched

Items are uniquely identified by: **`SKU-Size`**

```javascript
const itemKey = `${item.sku}-${item.size}`;
// Example: "SHIRT-001-M" or "PANTS-123-L"
```

Make sure:
- ✅ SKU is correct in cart items
- ✅ Size matches exactly (case-sensitive)
- ✅ Both fields present in cart data

---

## Verification Checklist

- [ ] Copy `CHECKOUT_UPDATED.tsx` to your project
- [ ] Test: Add item → Checkout → Pay → Verify cart empty
- [ ] Test: Add 3 items → Checkout 1 item → Verify 2 remain
- [ ] Test: Check localStorage in DevTools (F12)
- [ ] Test: Refresh page → Cart persists correctly

---

## Questions?

- **Q: Will this affect existing orders?**
  - A: No, only new checkouts use this code

- **Q: What if SKU has special characters?**
  - A: Still works, `sku-size` format is flexible

- **Q: What if item quantity is 2?**
  - A: Removes entire item (both units), not partial quantities
  
- **Q: Does backend need updates?**
  - A: No, backend is already correct (clears via `.items.all().delete()`)

---

All ready! Copy the file and test! 🚀
