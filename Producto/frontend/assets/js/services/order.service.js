// Servicio de pedidos
const OrderService = {
  create(tableId, guests, items) {
    return api('/orders/', { method: 'POST', body: { table_id: tableId, guests, items } });
  },
  addItem(orderId, productId, quantity, notes) {
    return api(`/orders/${orderId}/items`, { method: 'POST', body: { product_id: productId, quantity, notes } });
  },
  myActive() { return api('/orders/my-active'); },
  openOrders(branchId) { return api('/orders/open' + (branchId ? `?branch_id=${branchId}` : '')); },
  get(orderId) { return api(`/orders/${orderId}`); },
  close(orderId) { return api(`/orders/${orderId}/close`, { method: 'PUT' }); }
};
