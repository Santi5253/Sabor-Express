// Servicio de parametrización (administrador): users, branches, products, providers, tables
const AdminService = {
  list: (resource) => api(`/admin/${resource}/`),
  create: (resource, body) => api(`/admin/${resource}/`, { method: 'POST', body }),
  update: (resource, id, body) => api(`/admin/${resource}/${id}`, { method: 'PUT', body })
};

const TableService = {
  list: (branchId) => api('/tables/' + (branchId ? `?branch_id=${branchId}` : '')),
  create: (body) => api('/tables/', { method: 'POST', body }),
  update: (id, body) => api(`/tables/${id}`, { method: 'PUT', body })
};

const ProductService = {
  list: (branchId, onlyAvailable) => {
    const q = [];
    if (branchId) q.push(`branch_id=${branchId}`);
    if (onlyAvailable) q.push('only_available=true');
    return api('/admin/products/' + (q.length ? '?' + q.join('&') : ''));
  }
};

const BranchService = { list: () => api('/admin/branches/') };
