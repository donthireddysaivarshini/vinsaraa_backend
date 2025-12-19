# Frontend Order Status Display - Complete Implementation

## 1. Update API Service (`src/services/api.ts`)

Add auto-refresh for order status:

```typescript
// Get user orders with status
export async function getUserOrders() {
  try {
    const response = await axios.get('/api/orders/');
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error);
    throw error;
  }
}

// Refresh a specific order's status
export async function refreshOrderStatus(orderId: number) {
  try {
    const response = await axios.get(`/api/orders/${orderId}/status/`);
    return response.data;
  } catch (error) {
    console.error('Error refreshing order status:', error);
    throw error;
  }
}
```

---

## 2. Updated OrderHistory Component (`src/pages/OrderHistory.tsx`)

Complete component with real-time status tracking:

```typescript
import React, { useEffect, useState } from 'react';
import { getUserOrders, refreshOrderStatus } from '../services/api';
import { AlertCircle, CheckCircle, Truck, Package, RefreshCw } from 'lucide-react';

interface OrderItem {
  id: number;
  product_name: string;
  variant_label: string;
  price: string;
  quantity: number;
}

interface Order {
  id: number;
  total_amount: string;
  payment_status: 'Pending' | 'Paid';
  order_status: 'Processing' | 'Shipped' | 'Delivered';
  razorpay_order_id: string;
  created_at: string;
  shipping_address: string;
  phone: string;
  items: OrderItem[];
}

export default function OrderHistory() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState<number | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchOrders();
    
    // Auto-refresh every 30 seconds if enabled
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchOrders();
      }, 30000); // 30 seconds
    }
    
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await getUserOrders();
      // Show only PAID orders for customers
      const filteredOrders = data.filter((o: Order) => o.payment_status === 'Paid');
      setOrders(filteredOrders);
    } catch (error) {
      console.error('Failed to load orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshOrder = async (orderId: number) => {
    try {
      setRefreshing(orderId);
      const updatedOrderData = await refreshOrderStatus(orderId);
      
      // Update the order in local state
      setOrders(prevOrders =>
        prevOrders.map(order =>
          order.id === orderId
            ? {
                ...order,
                order_status: updatedOrderData.order_status,
                payment_status: updatedOrderData.payment_status,
              }
            : order
        )
      );
    } catch (error) {
      console.error('Error refreshing order:', error);
    } finally {
      setRefreshing(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Processing':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'Shipped':
        return <Truck className="w-5 h-5 text-blue-500" />;
      case 'Delivered':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return <Package className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'Shipped':
        return 'bg-blue-100 text-blue-800';
      case 'Delivered':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusMessage = (status: string) => {
    switch (status) {
      case 'Processing':
        return '📦 Your order is being prepared for shipment';
      case 'Shipped':
        return '🚚 Your order is on its way!';
      case 'Delivered':
        return '✅ Your order has been delivered!';
      default:
        return 'Order status unknown';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading orders...</p>
        </div>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 pt-20">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center py-12">
            <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 text-lg">No orders yet</p>
            <p className="text-gray-500">Your orders will appear here after you complete your first purchase.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Order History</h1>
          <div className="flex gap-4">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                autoRefresh
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              {autoRefresh ? '🔄 Auto-Refresh: ON' : '⏸️ Auto-Refresh: OFF'}
            </button>
            <button
              onClick={() => fetchOrders()}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 transition flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh Now
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {orders.map((order) => (
            <div key={order.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              {/* Order Header */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Order #</p>
                    <p className="font-semibold text-lg">{order.id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Date</p>
                    <p className="font-semibold">
                      {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total</p>
                    <p className="font-semibold text-lg">₹{parseFloat(order.total_amount).toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Payment</p>
                    <span className="inline-block px-3 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-800">
                      ✓ {order.payment_status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Order Status Progress */}
              <div className="px-6 py-6 border-b border-gray-200">
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(order.order_status)}
                      <p className="text-sm text-gray-600 font-semibold">Order Status</p>
                    </div>
                    <button
                      onClick={() => handleRefreshOrder(order.id)}
                      disabled={refreshing === order.id}
                      className="text-blue-500 hover:text-blue-700 disabled:opacity-50 transition"
                      title="Refresh status"
                    >
                      {refreshing === order.id ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                  <span
                    className={`inline-block px-4 py-2 rounded-full text-sm font-bold ${getStatusColor(
                      order.order_status
                    )}`}
                  >
                    {order.order_status}
                  </span>
                </div>
                <p className="text-gray-600">{getStatusMessage(order.order_status)}</p>

                {/* Status Timeline */}
                <div className="mt-4">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        ['Processing', 'Shipped', 'Delivered'].includes(order.order_status)
                          ? 'bg-green-500'
                          : 'bg-gray-300'
                      }`}
                    ></div>
                    <span className="text-sm font-semibold">Processing</span>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        ['Shipped', 'Delivered'].includes(order.order_status)
                          ? 'bg-green-500'
                          : 'bg-gray-300'
                      }`}
                    ></div>
                    <span className="text-sm font-semibold">Shipped</span>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        order.order_status === 'Delivered'
                          ? 'bg-green-500'
                          : 'bg-gray-300'
                      }`}
                    ></div>
                    <span className="text-sm font-semibold">Delivered</span>
                  </div>
                </div>
              </div>

              {/* Order Items */}
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="font-semibold text-lg mb-4">Items</h3>
                <div className="space-y-2">
                  {order.items.map((item) => (
                    <div
                      key={item.id}
                      className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0"
                    >
                      <div>
                        <p className="font-medium">{item.product_name}</p>
                        <p className="text-sm text-gray-600">{item.variant_label}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">₹{parseFloat(item.price).toFixed(2)}</p>
                        <p className="text-sm text-gray-600">Qty: {item.quantity}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Shipping Address */}
              <div className="px-6 py-4">
                <h3 className="font-semibold text-lg mb-2">Shipping Address</h3>
                <p className="text-gray-700 whitespace-pre-line text-sm">{order.shipping_address}</p>
                <p className="text-gray-700 text-sm mt-2">Phone: {order.phone}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## 3. Key Features Implemented

### ✅ **Auto-Refresh**
- Automatically refreshes order status every 30 seconds
- Toggle button to enable/disable auto-refresh
- Manual refresh button for immediate updates

### ✅ **Visual Status Indicators**
- Color-coded status badges:
  - 🟡 Yellow = Processing
  - 🔵 Blue = Shipped
  - 🟢 Green = Delivered
- Icons for each status
- Descriptive messages

### ✅ **Status Timeline**
- Shows all stages: Processing → Shipped → Delivered
- Visual dots indicate completed vs pending stages
- Customer sees progress at a glance

### ✅ **Real-time Updates**
- Click refresh button to check latest status
- Auto-refresh polls backend every 30 seconds
- No page reload needed
- Smooth animations

---

## 4. How Admin Changes Affect Frontend

### Admin Updates Status:
```
Admin Panel: Order #38 Status changed Processing → Shipped
    ↓
Backend: Saves order_status = 'Shipped'
    ↓
Frontend (Auto-refresh every 30s):
    ├─ Calls GET /api/orders/
    ├─ Gets updated order_status = 'Shipped'
    ├─ Updates local state
    └─ UI reflects change ✅
```

### Customer sees:
1. **Before refresh:** Order Status = Processing 🟡
2. **After refresh:** Order Status = Shipped 🔵
3. **Timeline updates:** Processing ✓ → Shipped ✓ → Delivered

---

## 5. Implementation Steps

1. **Copy the OrderHistory component** above
2. **Update api.ts** with the functions above
3. **Add route** in your router:
   ```typescript
   {
     path: '/orders',
     element: <OrderHistory />,
     requiredAuth: true
   }
   ```
4. **Add to navigation** link to `/orders`
5. **Test:**
   - Admin changes order status
   - Wait 30 seconds OR click "Refresh Now"
   - Frontend shows updated status ✅

---

## 6. API Response Format

Backend returns orders like this:

```json
[
  {
    "id": 38,
    "total_amount": "999.00",
    "payment_status": "Paid",
    "order_status": "Shipped",
    "created_at": "2025-12-19T10:30:00Z",
    "shipping_address": "123 Street\nCity, ST 12345",
    "phone": "+91234567890",
    "items": [
      {
        "id": 1,
        "product_name": "Product Name",
        "variant_label": "Size: M",
        "price": "999.00",
        "quantity": 1
      }
    ]
  }
]
```

---

## 7. Styling Customization

You can customize colors in the component:

```typescript
// Change auto-refresh interval (currently 30 seconds)
setInterval(() => {
  fetchOrders();
}, 30000); // Change 30000 to your preferred milliseconds

// Customize status colors
const getStatusColor = (status: string) => {
  switch (status) {
    case 'Processing':
      return 'bg-yellow-100 text-yellow-800';  // Customize here
    case 'Shipped':
      return 'bg-blue-100 text-blue-800';
    case 'Delivered':
      return 'bg-green-100 text-green-800';
  }
};
```

---

## 8. Summary

✅ **Displays order status** - Processing, Shipped, Delivered  
✅ **Auto-refreshes** - Every 30 seconds  
✅ **Manual refresh** - Click button for instant update  
✅ **Visual feedback** - Icons, colors, timeline  
✅ **Reflects admin changes** - Without page reload  
✅ **Clean UI** - Professional order tracking experience  

🎉 Ready to deploy!

