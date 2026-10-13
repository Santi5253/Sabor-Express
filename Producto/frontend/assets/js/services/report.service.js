// Servicio de reportes
const ReportService = {
  generate(branchId, dateFrom, dateTo) {
    return api('/reports/generate', { method: 'POST', body: { branch_id: branchId, date_from: dateFrom, date_to: dateTo } });
  },
  async export(branchId, dateFrom, dateTo) {
    const res = await api(`/reports/export?branch_id=${branchId}&date_from=${dateFrom}&date_to=${dateTo}`, { raw: true });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SaborExpress_Report_${dateFrom}_to_${dateTo}.xlsx`;
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  }
};
