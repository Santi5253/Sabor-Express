// Servicio de pagos
const PaymentService = {
  payCash(orderId, amountGiven) {
    return api('/payments/', { method: 'POST', body: { order_id: orderId, method: 'Cash', amount_given: amountGiven } });
  },
  payCard(orderId, method, lastFour, authNumber) {
    return api('/payments/', {
      method: 'POST',
      body: { order_id: orderId, method, last_four_digits: lastFour, authorization_number: authNumber }
    });
  }
};
