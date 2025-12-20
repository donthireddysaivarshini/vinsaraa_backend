# Updated Checkout - Remove Only Purchased Items

## 🎯 What Changed

Instead of clearing the **entire cart**, the checkout now removes **only the purchased items**, keeping any items added while checking out.

---

## 📝 Key Change in Payment Handler

### Before ❌
```javascript
// Cleared ENTIRE cart
localStorage.removeItem('cart');
```

### After ✅
```javascript
// Remove ONLY purchased items
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
```

---

## 🔄 How It Works

**Before Payment:**
```
Cart: [
  { sku: "SHIRT-001", size: "M", quantity: 2 },
  { sku: "SHIRT-002", size: "L", quantity: 1 }
]
```

**Checkout with SHIRT-001 (M) only:**
```
Purchased: [ { sku: "SHIRT-001", size: "M" } ]
```

**After Payment Success:**
```
Cart: [
  { sku: "SHIRT-002", size: "L", quantity: 1 }  ← Stays in cart!
]
```

---

## 🎯 Implementation

### 1. **Use Updated Checkout.tsx**
Replace your current `Checkout.tsx` with `CHECKOUT_UPDATED.tsx`

Key section (lines 264-290):
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
```

### 2. **Optional: Update CartContext (For React State Sync)**

If you want to keep React state in sync with localStorage, update your CartContext:

```typescript
// CartContext.tsx

interface CartContextType {
  cartItems: CartItem[];
  addToCart: (item: CartItem) => void;
  removeCartItem: (id: string, size: string) => void;
  removeMultipleItems: (items: Array<{sku: string, size: string}>) => void; // NEW
  clearCart: () => void;
  // ... other methods
}

export const CartProvider = ({ children }: { children: React.ReactNode }) => {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

  // NEW: Remove multiple items by SKU and size
  const removeMultipleItems = (items: Array<{sku: string, size: string}>) => {
    const updatedItems = cartItems.filter(item => {
      return !items.some(i => i.sku === item.sku && i.size === item.size);
    });
    
    setCartItems(updatedItems);
    localStorage.setItem('cart', JSON.stringify(updatedItems));
  };

  const value = {
    cartItems,
    removeMultipleItems,  // Add this
    // ... other methods
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};
```

Then in Checkout, use it:
```javascript
import { useCart } from "@/pages/CartContext";

const { removeMultipleItems } = useCart();

// In payment handler:
removeMultipleItems(
  payload.items.map(item => ({ 
    sku: item.sku, 
    size: item.size 
  }))
);
```

---

## 📊 Behavior Comparison

| Scenario | Old Behavior | New Behavior |
|----------|-------------|-------------|
| Checkout 1 item | Cart: empty | Cart: empty |
| Checkout partial items | Cart: **empty** ❌ | Cart: remaining items ✅ |
| Add item during checkout | Lost ❌ | Kept ✅ |
| Multiple purchases | Cleared each time ❌ | Only removes purchases ✅ |

---

## 🧪 Testing

### Test Case 1: Single Item Purchase
1. Add 1 item to cart
2. Checkout & pay
3. ✅ Cart should be empty

### Test Case 2: Multiple Items, Buy Some
1. Add 3 different items to cart
2. Checkout with 2 items
3. ✅ Cart should have 1 item remaining

### Test Case 3: Item Added During Checkout
1. Cart: [Item A]
2. Checkout starts
3. (Separately) Add Item B to cart
4. Complete payment for Item A
5. ✅ Cart should have [Item B]

---

## 📝 Code Location

**File**: `CHECKOUT_UPDATED.tsx` (lines 264-290)

**Section**: Payment Handler → Payment Success → "Remove Only Purchased Items from Cart"

---

## ✨ Benefits

- 🎁 Customers can add more items while checkout is in progress
- 🔄 Only purchased items removed (matches OrderItem behavior)
- 💾 Partial carts preserved
- 🧹 Clean, minimal code
- 🔀 No breaking changes to existing flows

---

## ⚠️ Important Notes

1. **SKU + Size Combo**: Items are identified by `SKU-Size` combination
2. **Case Sensitive**: Make sure SKU case matches exactly
3. **localStorage Sync**: React state updates via CartContext (if implemented)
4. **Backward Compatible**: Works with existing cart structure

---

## 🚀 Next Steps

1. Copy `CHECKOUT_UPDATED.tsx` → `src/pages/Checkout.tsx`
2. (Optional) Update CartContext with `removeMultipleItems`
3. Test all 3 scenarios above
4. Commit and deploy!

All set! 🎉
