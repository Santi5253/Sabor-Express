// Servicio de autenticación
const AuthService = {
  async login(email, password, remember) {
    const data = await api('/auth/login', { method: 'POST', body: { email, password, remember } });
    setSession(data);
    return data;
  },
  async me() {
    return api('/auth/me');
  },
  logout() { logout(); }
};
