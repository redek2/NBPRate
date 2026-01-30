import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { RatesService } from './rates.service';
import { environment } from '../../environments/environment';
import { Currency, Rate } from '../models/rate.models';

describe('RatesService', () => {
  let service: RatesService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        RatesService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });
    service = TestBed.inject(RatesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // Weryfikacja, czy nie zostały żadne wiszące zapytania
    httpMock.verify();
  });

  it('powinien pobrać listę walut (GET /currencies)', () => {
    const dummyCurrencies: Currency[] = [
      { id: 1, code: 'USD', name: 'Dolar' },
      { id: 2, code: 'EUR', name: 'Euro' }
    ];

    service.getCurrencies().subscribe(currencies => {
      expect(currencies.length).toBe(2);
      expect(currencies).toEqual(dummyCurrencies);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/currencies`);
    expect(req.request.method).toBe('GET');
    req.flush(dummyCurrencies);
  });

  it('powinien pobrać kursy historyczne (GET /rates/...)', () => {
    const dummyRates: Rate[] = [
      { date: '2024-01-01', value: 3.99, currency_code: 'USD' }
    ];

    service.getRates('USD', '2024-01-01', '2024-01-05').subscribe(rates => {
      expect(rates.length).toBe(1);
      expect(rates[0].value).toBe(3.99);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/rates/USD/2024-01-01/2024-01-05`);
    expect(req.request.method).toBe('GET');
    req.flush(dummyRates);
  });

  it('powinien obsłużyć błąd 404', () => {
    service.getRates('XXX', '2024-01-01', '2024-01-05').subscribe({
      next: () => fail('Powinien wystąpić błąd'),
      error: (error) => {
        expect(error.message).toContain('Server Error: 404');
      }
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/rates/XXX/2024-01-01/2024-01-05`);
    req.flush('Not Found', { status: 404, statusText: 'Not Found' });
  });
});