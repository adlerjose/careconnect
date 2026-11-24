const timeFormatter = new Intl.DateTimeFormat('pt-BR', {
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
});

export function formatTime(date: Date | null): string {
  return date ? timeFormatter.format(date) : '—';
}

const ENVIRONMENT_LABELS: Record<string, string> = {
  development: 'Desenvolvimento',
  staging: 'Homologação',
  production: 'Produção',
  test: 'Teste',
};

export function formatEnvironment(env: string | undefined): string {
  if (!env) return '—';
  return ENVIRONMENT_LABELS[env.toLowerCase()] ?? env;
}

/**
 * Mascara um número de WhatsApp para reduzir exposição de dados pessoais,
 * mantendo apenas os 4 últimos dígitos visíveis.
 */
export function maskPhone(value: string): string {
  const digits = value.replace(/\D/g, '');
  if (digits.length <= 4) return digits;
  return `${'•'.repeat(Math.max(digits.length - 4, 0))}${digits.slice(-4)}`;
}
