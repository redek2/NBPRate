import { transformRatesToTree } from './rate-transformer';
import { Rate } from '../models/rate.models';

describe('RateTransformer', () => {
  it('powinien poprawnie pogrupować płaską listę w strukturę Rok -> Kwartał -> Miesiąc', () => {
    const inputRates: Rate[] = [
      { date: '2024-01-15', value: 4.0, currency_code: 'USD' }, // I Kwartał, Styczeń
      { date: '2024-04-10', value: 4.1, currency_code: 'USD' }  // II Kwartał, Kwiecień
    ];

    const result = transformRatesToTree(inputRates);

    // Sprawdzenie Roku
    expect(result.length).toBe(1);
    expect(result[0].year).toBe(2024);

    // Sprawdzenie Kwartałów (powinny być 2 różne)
    expect(result[0].quarters.length).toBe(2);
    expect(result[0].quarters[0].quarterName).toBe('I Kwartał');
    expect(result[0].quarters[1].quarterName).toBe('II Kwartał');

    // Sprawdzenie Miesiąca w I kwartale
    const q1 = result[0].quarters[0];
    expect(q1.months.length).toBe(1);
    expect(q1.months[0].monthName).toBe('Styczeń');
    expect(q1.months[0].rates.length).toBe(1);
    expect(q1.months[0].rates[0].value).toBe(4.0);
  });

  it('powinien posortować daty chronologicznie', () => {
    const inputRates: Rate[] = [
      { date: '2024-02-01', value: 1, currency_code: 'USD' },
      { date: '2024-01-01', value: 1, currency_code: 'USD' }
    ];

    const result = transformRatesToTree(inputRates);
    const months = result[0].quarters[0].months;
    
    expect(months[0].monthName).toBe('Styczeń');
    expect(months[1].monthName).toBe('Luty');
  });
});