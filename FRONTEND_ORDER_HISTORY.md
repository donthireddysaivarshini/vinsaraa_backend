# Frontend Order History Implementation

## 1. Update your `api.ts` service

Add these functions to your API service:

```typescript
// Get all user orders
export async function getUserOrders() {
  try {
    const response = await axios.get('/api/orders/');
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error);
    throw error;
  }
}

// Get specific order details
export async function getOrderDetails(orderId: number) {
  try {
    const response = await axios.get(`/api/orders/${orderId}/status/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching order details:', error);
    throw error;
  }
}

// Admin: Update order status (only for admin users)
export async function updateOrderStatus(orderId: number, newStatus: string) {
  try {
    const response = await axios.patch(`/api/orders/${orderId}/update-status/`, {
      order_status: newStatus
    });
    return response.data;
  } catch (error) {
    console.error('Error updating order status:', error);
    throw error;
  }
}
```

---

## 2. Create OrderHistory Component

Create a new file: `src/pages/OrderHistory.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { getUserOrders, updateOrderStatus } from '../services/api';
import { AlertCircle, CheckCircle, Truck, Package } from 'lucide-react';

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
  const [updating, setUpdating] = useState<number | null>(null);
  const isAdmin = localStorage.getItem('isAdmin') === 'true'; // Add this to your auth logic

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await getUserOrders();
      // Filter to show only PAID orders for customers
      const filteredOrders = isAdmin ? data : data.filter((o: Order) => o.payment_status === 'Paid');
      setOrders(filteredOrders);
    } catch (error) {
      console.error('Failed to load orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (orderId: number, newStatus: string) => {
    try {
      setUpdating(orderId);
      await updateOrderStatus(orderId, newStatus);
      // Refresh orders list
      fetchOrders();
    } catch (error: any) {
      console.error('Error:', error.response?.data?.detail || error.message);
      alert(error.response?.data?.detail || 'Failed to update status');
    } finally {
      setUpdating(null);
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

  const getPaymentStatusColor = (status: string) => {
    return status === 'Paid'
      ? 'bg-green-100 text-green-800'
      : 'bg-yellow-100 text-yellow-800';
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
        <h1 className="text-3xl font-bold mb-8">Order History</h1>

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
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getPaymentStatusColor(
                        order.payment_status
                      )}`}
                    >
                      {order.payment_status}
                    </span>
                  </div>
                </div>
              </div>

              {/* Order Items */}
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="font-semibold text-lg mb-4">Items</h3>
                <div className="space-y-2">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
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

              {/* Order Status Section */}
              <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(order.order_status)}
                    <div>
                      <p className="text-sm text-gray-600">Order Status</p>
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(
                          order.order_status
                        )}`}
                      >
                        {order.order_status}
                      </span>
                    </div>
                  </div>

                  {/* Admin Status Update Dropdown */}
                  {isAdmin && order.payment_status === 'Paid' && (
                    <select
                      value={order.order_status}
                      onChange={(e) => handleStatusChange(order.id, e.target.value)}
                      disabled={updating === order.id}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <option value="Processing">Processing</option>
                      <option value="Shipped">Shipped</option>
                      <option value="Delivered">Delivered</option>
                    </select>
                  )}

                  {isAdmin && order.payment_status === 'Pending' && (
                    <p className="text-sm text-yellow-600 font-medium">
                      ⏳ Awaiting payment
                    </p>
                  )}
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

## 3. Add Route to your Router

Update your `src/App.tsx` or router configuration:

```typescript
import OrderHistory from './pages/OrderHistory';

const routes = [
  // ... other routes
  {
    path: '/orders',
    element: <OrderHistory />,
    requiredAuth: true
  }
];
```

---

## 4. Update Authentication Logic

In your login/auth handler, save the `isAdmin` flag:

```typescript
// In your Login.tsx or auth service
const handleLoginSuccess = (response: any) => {
  localStorage.setItem('userToken', response.data.access);
  localStorage.setItem('isAdmin', response.data.user?.is_staff ? 'true' : 'false');
  // ... other logic
};
```

---

## 5. Add Link to Navigation

Update your navigation component to link to order history:

```typescript
<Link to="/orders" className="nav-link">
  My Orders
</Link>
```

---

## Backend API Response Format

The backend now returns orders in this format:

```json
{
  "id": 1,
  "total_amount": "5999.00",
  "payment_status": "Paid",
  "order_status": "Processing",
  "razorpay_order_id": "order_xyz",
  "razorpay_payment_id": "pay_xyz",
  "created_at": "2025-12-19T10:30:00Z",
  "shipping_address": "123 Street\nApt 5\nCity, ST 12345\nCountry",
  "phone": "+91234567890",
  "items": [
    {
      "id": 1,
      "product_name": "Product Name",
      "variant_label": "Size: M",
      "price": "999.00",
      "quantity": 2
    }
  ]
}
```

---

## Key Features

✅ Displays all user's paid orders  
✅ Shows order status (Processing → Shipped → Delivered)  
✅ Admin can only update status if payment is Paid  
✅ Shows pending orders only to admin  
✅ Real-time status updates  
✅ Responsive design  
✅ Clear visual status indicators  

